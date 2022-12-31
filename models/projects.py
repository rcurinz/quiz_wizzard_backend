from . import db
from .bases import Model, BaseConstant

class Projects(Model):
    __tablename__ = 'projects'
    # COLUMNS
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    id_user = db.Column(db.BigInteger)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    dir = db.Column(db.String(255))
    status = db.Column(db.String(255))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

    def __init__(self, id_user, name, description, dir, status, created_at, updated_at, deleted_at):
        self.name = name
        self.id_user = id_user
        self.description = description
        self.status = status
        self.dir = dir
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at