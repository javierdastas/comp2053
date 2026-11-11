"""Aplicación didáctica local: una persona operadora gestiona datos ficticios."""
import os
import re
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from sqlalchemy import URL, func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.exceptions import HTTPException

from models import Persona, Recurso, Reserva, db

PROYECTOS = {
    "salas": {"titulo": "Reservas de salas", "recurso": "Sala", "categoria": "Tipo de sala"},
    "equipos": {"titulo": "Préstamo de computadoras", "recurso": "Computadora", "categoria": "Tipo de equipo"},
    "tutorias": {"titulo": "Citas de tutoría", "recurso": "Tutor o tutora", "categoria": "Materia"},
}
ZONA = ZoneInfo("America/Puerto_Rico")
HORAS = range(8, 17)  # Nueve bloques: 08:00–09:00 hasta 16:00–17:00.


def ahora():
    # Convención del proyecto: DATETIME local de Puerto Rico, sin conversión del navegador.
    return datetime.now(ZONA).replace(tzinfo=None)


class EntradaInvalida(ValueError):
    pass


def datos_json():
    if not request.is_json:
        raise EntradaInvalida("Envía JSON con Content-Type application/json.")
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        raise EntradaInvalida("El cuerpo debe ser un objeto JSON válido.")
    return datos


def texto(datos, campo, minimo, maximo):
    valor = datos.get(campo)
    if not isinstance(valor, str) or not minimo <= len(valor.strip()) <= maximo:
        raise EntradaInvalida(f"{campo}: escribe entre {minimo} y {maximo} caracteres.")
    return valor.strip()


def entero(valor, campo):
    if isinstance(valor, bool) or not re.fullmatch(r"[1-9][0-9]{0,9}", str(valor)):
        raise EntradaInvalida(f"{campo}: selecciona una opción válida.")
    return int(valor)


def fecha_valida(valor):
    try:
        if not isinstance(valor, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", valor):
            raise ValueError
        dia = date.fromisoformat(valor)
    except ValueError:
        raise EntradaInvalida("fecha: usa el formato AAAA-MM-DD.") from None
    hoy = ahora().date()
    if not hoy <= dia <= hoy + timedelta(days=30):
        raise EntradaInvalida("fecha: elige desde hoy hasta los próximos 30 días.")
    return dia


def limites(dia):
    inicio = datetime.combine(dia, time.min)
    return inicio, inicio + timedelta(days=1)


def create_app(test_config=None):
    load_dotenv()
    app = Flask(__name__)
    proyecto = os.getenv("PROYECTO", "salas")
    if proyecto not in PROYECTOS:
        raise ValueError("PROYECTO debe ser salas, equipos o tutorias.")
    app.config.update(
        PROYECTO=proyecto,
        MAX_CONTENT_LENGTH=16384,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_DATABASE_URI=URL.create(
            "mysql+pymysql", username=os.getenv("DB_USER", "fullstack_app"),
            password=os.getenv("DB_PASSWORD", ""), host=os.getenv("DB_HOST", "127.0.0.1"),
            port=int(os.getenv("DB_PORT", "3306")),
            database=os.getenv("DB_NAME", f"fullstack_{proyecto}"),
            query={"charset": "utf8mb4"},
        ),
    )
    if test_config:
        app.config.update(test_config)
    db.init_app(app)

    @app.errorhandler(EntradaInvalida)
    def entrada_invalida(error):
        return jsonify(error=str(error)), 400

    @app.errorhandler(HTTPException)
    def error_http(error):
        return jsonify(error=error.description), error.code

    @app.errorhandler(SQLAlchemyError)
    def error_bd(error):
        db.session.rollback()
        app.logger.exception("No se pudo completar la operación de base de datos")
        return jsonify(error="No se pudo acceder a la base de datos. Verifica el servicio."), 503

    @app.get("/")
    def index():
        hoy = ahora().date()
        return render_template("index.html", config=PROYECTOS[app.config["PROYECTO"]],
                               hoy=hoy.isoformat(), max_fecha=(hoy + timedelta(days=30)).isoformat())

    @app.get("/api/personas")
    def personas():
        filas = db.session.scalars(select(Persona).order_by(Persona.nombre)).all()
        return jsonify([{"id": p.id, "nombre": p.nombre, "email": p.email} for p in filas])

    @app.post("/api/personas")
    def crear_persona():
        datos = datos_json()
        nombre = texto(datos, "nombre", 2, 80)
        email = texto(datos, "email", 5, 120).lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            raise EntradaInvalida("email: escribe una dirección como nombre@example.org.")
        persona = Persona(nombre=nombre, email=email)
        db.session.add(persona)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify(error="Ese correo ya está registrado. Selecciona la persona existente."), 409
        return jsonify(id=persona.id, nombre=persona.nombre, email=persona.email), 201

    @app.get("/api/recursos")
    def recursos():
        filas = db.session.scalars(select(Recurso).order_by(Recurso.nombre)).all()
        return jsonify([{"id": r.id, "nombre": r.nombre, "categoria": r.categoria} for r in filas])

    @app.get("/api/disponibilidad")
    def disponibilidad():
        dia = fecha_valida(request.args.get("fecha"))
        rid = entero(request.args.get("recurso_id"), "recurso_id")
        if db.session.get(Recurso, rid) is None:
            return jsonify(error="El recurso no existe."), 404
        desde, hasta = limites(dia)
        ocupadas = set(db.session.scalars(select(Reserva.inicio).where(
            Reserva.recurso_id == rid, Reserva.inicio >= desde, Reserva.inicio < hasta)).all())
        actual = ahora()
        bloques = []
        for hora in HORAS:
            inicio = datetime.combine(dia, time(hora))
            estado = "Pasó" if inicio <= actual else "Ocupado" if inicio in ocupadas else "Disponible"
            bloques.append({"hora": f"{hora:02d}:00", "disponible": estado == "Disponible", "estado": estado})
        return jsonify(bloques)

    @app.get("/api/reservas")
    def reservas():
        dia = fecha_valida(request.args.get("fecha"))
        desde, hasta = limites(dia)
        consulta = select(Reserva).where(Reserva.inicio >= desde, Reserva.inicio < hasta)
        if request.args.get("recurso_id"):
            consulta = consulta.where(Reserva.recurso_id == entero(request.args["recurso_id"], "recurso_id"))
        return jsonify([r.to_dict() for r in db.session.scalars(consulta.order_by(Reserva.inicio, Reserva.id)).all()])

    @app.post("/api/reservas")
    def crear_reserva():
        datos = datos_json()
        pid = entero(datos.get("persona_id"), "persona_id")
        rid = entero(datos.get("recurso_id"), "recurso_id")
        dia = fecha_valida(datos.get("fecha"))
        hora = datos.get("hora")
        if hora not in [f"{h:02d}:00" for h in HORAS]:
            raise EntradaInvalida("hora: selecciona un bloque entre 08:00 y 16:00.")
        inicio = datetime.combine(dia, time.fromisoformat(hora))
        if inicio <= ahora():
            raise EntradaInvalida("hora: selecciona un bloque futuro.")
        motivo = texto(datos, "motivo", 5, 200)
        if db.session.get(Persona, pid) is None or db.session.get(Recurso, rid) is None:
            return jsonify(error="La persona o el recurso no existe. Actualiza las listas."), 404
        reserva = Reserva(persona_id=pid, recurso_id=rid, inicio=inicio, motivo=motivo)
        db.session.add(reserva)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify(error="Conflicto: la persona o el recurso ya tiene una reserva a esa hora."), 409
        return jsonify(reserva.to_dict()), 201

    @app.delete("/api/reservas/<int:reserva_id>")
    def cancelar_reserva(reserva_id):
        reserva = db.session.get(Reserva, reserva_id)
        if reserva is None:
            return jsonify(error="La reserva no existe. Actualiza la lista."), 404
        if reserva.inicio <= ahora():
            raise EntradaInvalida("Solo se cancelan reservas futuras.")
        db.session.delete(reserva)
        db.session.commit()
        return "", 204

    @app.get("/api/resumen")
    def resumen():
        dia = fecha_valida(request.args.get("fecha"))
        desde, hasta = limites(dia)
        conteos = dict(db.session.execute(select(Reserva.recurso_id, func.count(Reserva.id))
            .where(Reserva.inicio >= desde, Reserva.inicio < hasta).group_by(Reserva.recurso_id)).all())
        filas = db.session.scalars(select(Recurso).order_by(Recurso.nombre)).all()
        por_recurso = [{"recurso": r.nombre, "reservas": conteos.get(r.id, 0)} for r in filas]
        total = sum(conteos.values())
        capacidad = len(filas) * len(HORAS)
        return jsonify(fecha=dia.isoformat(), total=total, capacidad=capacidad,
                       porcentaje=round(total * 100 / capacidad, 1) if capacidad else 0,
                       por_recurso=por_recurso)

    return app
