import json
from flask import (Blueprint, jsonify, request)
from flask_cors import CORS
from werkzeug.utils import secure_filename

from app import app
from reports.api_project_reports import *

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
mod_api_project = Blueprint('api_project', __name__, template_folder='templates', url_prefix='/api')



#test
@mod_api_project.route('/test')
def test():
    data = prueba()
    return jsonify(data)


@mod_api_project.route('/generate', methods=['POST'])
def Generate():
    data = request.data.decode('utf-8')
    frases = generate(data)
    print(frases)
    return jsonify(frases)


@mod_api_project.route('/uploads', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        respuesta = Upload_files(f)
        return jsonify(respuesta), 200
    else:
        return jsonify({"message": "Error al subir el archivo"}), 500


#Login
@mod_api_project.route('/login', methods=['POST'])
def login():
    data = request.data.decode('utf-8')
    data = json.loads(data)
    user = data['email']
    password = data['password']
    data = login_user(user, password)
    return jsonify(data)


#registrar usuario
@mod_api_project.route('/register', methods=['POST'])
def register():
    data = request.data.decode('utf-8')
    data = json.loads(data)
    data = register_user(data)
    return jsonify(data)

