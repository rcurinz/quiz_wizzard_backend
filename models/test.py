from datetime import datetime
from sqlalchemy.orm import relationship
from . import db
from .bases import Model, BaseConstant
from .associations import file_test_association


class Test(Model):
    __tablename__ = 'tests'
    test_id = db.Column(db.Integer, primary_key=True)
    #proyecto_id = db.Column(db.Integer, db.ForeignKey('proyectos.project_id'))
    #file_id = db.Column(db.Integer, db.ForeignKey('archivos.file_id'), nullabl=True)  # Nueva columna
    archivos = relationship("Archivo", secondary=file_test_association)
    names_files = db.Column(db.Text)
    proyecto_id = db.Column(db.Integer, nullable=True)
    file_id = db.Column(db.Integer, nullable=True)  # Nueva columna
    test_data = db.Column(db.Text)  # Asume que los datos del test son una cadena, modifícalo según tus necesidades
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    is_multi_file = db.Column(db.Boolean, default=False)