from datetime import datetime
from sqlalchemy.orm import relationship
from . import db
from .bases import Model, BaseConstant
from .associations import file_test_association

class Archivo(Model):
    __tablename__ = 'archivos'
    file_id = db.Column(db.Integer, primary_key=True)
    #project_id = db.Column(db.Integer, db.ForeignKey('proyectos.project_id'))
    project_id = db.Column(db.Integer, nullable=True)
    filename = db.Column(db.String(255))
    original_filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # relación muchos a muchos con tests
    tests = relationship("Test", secondary=file_test_association)
    #cuestionarios = db.relationship('Test', backref='archivo') # Nueva relación