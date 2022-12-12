from . import db
from .bases import Model, BaseConstant


class Test(Model):
    __tablename__ = 'test'
    # COLUMNS
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True) #que inicie con uno
    name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)