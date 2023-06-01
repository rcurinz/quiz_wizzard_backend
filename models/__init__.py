from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#Models
#from .users import *
#from .projects import *
#from .files_user import *
#from .quiz_file_user import *

# nuevos modelos on GPT
from .Archivo import *
from .Proyecto import *
from .Usuario import *
from .Test import *
from .Token import *