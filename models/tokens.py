from . import db
from .bases import Model, BaseConstant

class Tokens(Model):
    __tablename__ = 'tokens'
    # COLUMNS
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    token = db.Column(db.String(255))
    id_user = db.Column(db.BigInteger)
    status_token = db.Column(db.String(255))
    start_at = db.Column(db.DateTime)
    finish_at = db.Column(db.DateTime)

    def __init__(self, token, id_user, status_token, start_at, finish_at):
        self.token = token
        self.id_user = id_user
        self.status_token = status_token
        self.start_at = start_at
        self.finish_at = finish_at