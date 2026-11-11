"""Pruebas aisladas. SQLite en memoria NO reemplaza la prueba final en MySQL/MariaDB."""
import sys
from datetime import datetime
from pathlib import Path

import pytest
from sqlalchemy import event

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app as modulo
from models import Persona, Recurso, Reserva, db


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setattr(modulo, "ahora", lambda: datetime(2030, 4, 1, 10, 30))
    aplicacion = modulo.create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://"})
    with aplicacion.app_context():
        @event.listens_for(db.engine, "connect")
        def claves_foraneas(conexion, _):
            conexion.execute("PRAGMA foreign_keys=ON")
        db.create_all()
        db.session.add_all([Persona(nombre="Uno", email="uno@example.org"),
                            Persona(nombre="Dos", email="dos@example.org"),
                            Recurso(nombre="Recurso A", categoria="Tipo A"),
                            Recurso(nombre="Recurso B", categoria="Tipo B")])
        db.session.commit()
    with aplicacion.test_client() as c:
        yield c
    with aplicacion.app_context():
        db.session.remove()
        db.drop_all()


def reserva(**cambios):
    datos = dict(persona_id=1, recurso_id=1, fecha="2030-04-02", hora="09:00", motivo="Estudiar Python")
    return datos | cambios


def test_ciclo_completo(client):
    assert client.get("/").status_code == 200
    r = client.post("/api/reservas", json=reserva())
    assert r.status_code == 201
    rid = r.json["id"]
    assert client.get("/api/reservas?fecha=2030-04-02").json[0]["motivo"] == "Estudiar Python"
    resumen = client.get("/api/resumen?fecha=2030-04-02").json
    assert (resumen["total"], resumen["capacidad"], resumen["porcentaje"]) == (1, 18, 5.6)
    assert len(resumen["por_recurso"]) == 2
    assert client.delete(f"/api/reservas/{rid}").status_code == 204
    assert client.get("/api/resumen?fecha=2030-04-02").json["total"] == 0
    assert client.post("/api/reservas", json=reserva()).status_code == 201


def test_conflicto_recurso(client):
    assert client.post("/api/reservas", json=reserva()).status_code == 201
    assert client.post("/api/reservas", json=reserva(persona_id=2)).status_code == 409
    # El rollback permite guardar la próxima transacción válida.
    assert client.post("/api/reservas", json=reserva(persona_id=2, hora="10:00")).status_code == 201


def test_conflicto_persona(client):
    client.post("/api/reservas", json=reserva())
    assert client.post("/api/reservas", json=reserva(recurso_id=2)).status_code == 409


@pytest.mark.parametrize("cambios", [
    {"fecha": "2030-03-31"}, {"fecha": "2030-05-02"}, {"fecha": "2030-02-30"},
    {"fecha": None}, {"fecha": "20300402"}, {"hora": "09:30"}, {"hora": "17:00"},
    {"fecha": "2030-04-01", "hora": "10:00"}, {"motivo": "  "}, {"motivo": "x" * 201},
    {"persona_id": True}, {"persona_id": 1.5}, {"recurso_id": 0}, {"recurso_id": None},
])
def test_entradas_invalidas(client, cambios):
    assert client.post("/api/reservas", json=reserva(**cambios)).status_code == 400


def test_ids_inexistentes(client):
    assert client.post("/api/reservas", json=reserva(persona_id=999)).status_code == 404
    assert client.delete("/api/reservas/999").status_code == 404


def test_personas_y_normalizacion(client):
    p = client.post("/api/personas", json={"nombre": "  Ana  ", "email": " ANA@EXAMPLE.ORG "})
    assert p.status_code == 201
    assert (p.json["nombre"], p.json["email"]) == ("Ana", "ana@example.org")
    assert client.post("/api/personas", json={"nombre": "Ana", "email": "ana@example.org"}).status_code == 409
    assert client.post("/api/personas", json={"nombre": "Ana", "email": "correo"}).status_code == 400


def test_json_malformado(client):
    assert client.post("/api/personas", data="{", content_type="application/json").status_code == 400
    assert client.post("/api/personas", json=[]).status_code == 400
    assert client.post("/api/personas", data="nombre=Ana").status_code == 400


def test_disponibilidad_y_filtro(client):
    client.post("/api/reservas", json=reserva())
    bloques = client.get("/api/disponibilidad?fecha=2030-04-02&recurso_id=1").json
    assert len(bloques) == 9
    assert next(b for b in bloques if b["hora"] == "09:00")["estado"] == "Ocupado"
    assert client.get("/api/reservas?fecha=2030-04-02&recurso_id=2").json == []
    hoy = client.get("/api/disponibilidad?fecha=2030-04-01&recurso_id=1").json
    assert hoy[0]["estado"] == "Pasó"
    assert client.get("/api/disponibilidad?fecha=2030-04-02&recurso_id=999").status_code == 404


def test_cancelacion_pasada(client):
    with client.application.app_context():
        r = Reserva(persona_id=1, recurso_id=1, inicio=datetime(2030, 4, 1, 8), motivo="Clase previa")
        db.session.add(r)
        db.session.commit()
        rid = r.id
    assert client.delete(f"/api/reservas/{rid}").status_code == 400


def test_claves_foraneas_y_tres_tablas(client):
    from sqlalchemy import inspect
    from sqlalchemy.exc import IntegrityError
    with client.application.app_context():
        assert set(inspect(db.engine).get_table_names()) == {"personas", "recursos", "reservas"}
        db.session.add(Reserva(persona_id=999, recurso_id=1, inicio=datetime(2030, 4, 2, 8), motivo="Prueba FK"))
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()
