from . import db
from .bases import Model, BaseConstant

class FilesUser(Model):
    __tablename__ = 'files_user'
    # COLUMNS
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    id_user = db.Column(db.BigInteger)
    id_file = db.Column(db.BigInteger)
    id_project = db.Column(db.BigInteger)
    name = db.Column(db.String(255))
    original_name = db.Column(db.String(500))
    description = db.Column(db.String(255))
    dir = db.Column(db.String(255))
    status = db.Column(db.String(255))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

    def __init__(self, id_user, name, dir, created_at, id_file, id_project):
        self.name = name
        self.id_user = id_user
        self.dir = dir
        self.created_at = created_at
        self.id_file = self.id_file
        self.id_project = self.id_project
