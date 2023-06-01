from datetime import datetime

from . import db
from .bases import Model, BaseConstant


class Test(Model):
    __tablename__ = 'tests'
    test_id = db.Column(db.Integer, primary_key=True)
    proyecto_id = db.Column(db.Integer, db.ForeignKey('proyectos.project_id'))
    test_data = db.Column(db.Text)  # Asume que los datos del test son una cadena, modifícalo según tus necesidades
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)