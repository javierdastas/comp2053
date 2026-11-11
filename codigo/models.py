"""Las tres clases representan exactamente las tres tablas del proyecto."""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Persona(db.Model):
    __tablename__ = "personas"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)


class Recurso(db.Model):
    __tablename__ = "recursos"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False, unique=True)
    categoria = db.Column(db.String(60), nullable=False)


class Reserva(db.Model):
    __tablename__ = "reservas"
    id = db.Column(db.Integer, primary_key=True)
    persona_id = db.Column(db.Integer, db.ForeignKey("personas.id"), nullable=False)
    recurso_id = db.Column(db.Integer, db.ForeignKey("recursos.id"), nullable=False)
    inicio = db.Column(db.DateTime, nullable=False)
    motivo = db.Column(db.String(200), nullable=False)
    __table_args__ = (
        db.UniqueConstraint("recurso_id", "inicio", name="uq_recurso_inicio"),
        db.UniqueConstraint("persona_id", "inicio", name="uq_persona_inicio"),
    )
    persona = db.relationship("Persona")
    recurso = db.relationship("Recurso")

    def to_dict(self):
        return {
            "id": self.id,
            "persona_id": self.persona_id,
            "persona": self.persona.nombre,
            "recurso_id": self.recurso_id,
            "recurso": self.recurso.nombre,
            "categoria": self.recurso.categoria,
            "inicio": self.inicio.isoformat(timespec="minutes"),
            "motivo": self.motivo,
        }
