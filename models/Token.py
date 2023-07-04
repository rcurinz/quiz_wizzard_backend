from datetime import datetime

from . import db
from .bases import Model, BaseConstant

class Token(Model):
    __tablename__ = 'tokens'
    token_id = db.Column(db.Integer, primary_key=True)
    #user_id = db.Column(db.Integer, db.ForeignKey('usuarios.user_id'))
    user_id = db.Column(db.Integer)
    token = db.Column(db.String(255))
    status_token = db.Column(db.String(50))  # Asume que status_token es una cadena corta, cambia según tus necesidades
    start_at = db.Column(db.DateTime, default=datetime.utcnow)
    finish_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    #user = db.relationship('Usuario', backref='tokens')