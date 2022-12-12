from . import db
from .bases import Model, BaseConstant

class Users(Model):
    __tablename__ = 'users'
    # COLUMNS
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    role = db.Column(db.String(255))
    email = db.Column(db.String(255))
    password = db.Column(db.String(255))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

    def __init__(self, name, last_name, role, email, password, created_at, updated_at, deleted_at):
        self.name = name
        self.last_name = last_name
        self.role = role
        self.email = email
        self.password = password
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at