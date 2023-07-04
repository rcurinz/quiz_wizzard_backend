from datetime import datetime

from . import db
from .bases import Model, BaseConstant

class Usuario(Model):
    __tablename__ = 'usuarios'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    name_user = db.Column(db.String(255))
    password = db.Column(db.String(255))  # Asegúrate de que las contraseñas se almacenan de forma segura (no texto plano)
    email = db.Column(db.String(255), unique=True)  # Opcional
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    #proyectos = db.relationship('Proyecto', backref='usuario')