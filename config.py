# JSON PRETTY PRINT
JSONIFY_PRETTYPRINT_REGULAR = False

# SECRET KEY HASHIDS
HASHID_SECRET_KEY = 'HASHID_SECRET_KEY'
# HASHID Alphabet, 16 charcters minimum
HASHID_ALPHABET = 'HASHID_ALPHABET'

# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
#THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

# Use a secure, unique and absolutely secret key for
# signing the data.
# cat /dev/urandom | base64 | head -c 16; echo
CSRF_SESSION_KEY = 'CSRF_SESSION_KEY'
# Secret key for signing cookies
SECRET_KEY = 'SECRET_KEY'

# Output SQL querys
SQLALCHEMY_ECHO = False
# For Signals
SQLALCHEMY_TRACK_MODIFICATIONS = True

# DATABASE
# MySQL
#SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:<PASSWORD>@localhost/transquest?charset=utf8mb4'
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/transquest?charset=utf8mb4'

SERVER_NAME = 'localhost:5000'
APPLICATION_ROOT = '/'

UPLOADS = 'uploads'