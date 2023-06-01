from datetime import datetime

from . import db
from .bases import Model, BaseConstant

class Archivo(Model):
    __tablename__ = 'archivos'
    file_id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('proyectos.project_id'))
    filename = db.Column(db.String(255))
    original_filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)