from sqlalchemy import Table, Column, Integer, ForeignKey
from . import db

# Tabla de asociación
file_test_association = Table('file_test_association', db.Model.metadata,
    Column('test_id', Integer, ForeignKey('tests.test_id')),
    Column('file_id', Integer, ForeignKey('archivos.file_id'))
)