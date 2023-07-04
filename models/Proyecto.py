from datetime import datetime
from . import db
from .bases import Model, BaseConstant

class Proyecto(Model):
    __tablename__ = 'proyectos'
    project_id = db.Column(db.Integer, primary_key=True)
    # user_id = db.Column(db.Integer, db.ForeignKey('usuarios.user_id'))
    user_id = db.Column(db.Integer)
    project_name = db.Column(db.String(255))
    description = db.Column(db.String(500),nullable=True)
    status = db.Column(db.String(50),nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    #archivos = db.relationship('Archivo', backref='proyecto')
    #tests = db.relationship('Test', backref='proyecto')