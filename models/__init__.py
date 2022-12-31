from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#Models
from .test import *
from .users import *
from .tokens import *
from .projects import *