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


@mod_api_project.route('/generate_answer', methods=['POST'])
def Generate_answer():
    data = request.data.decode('utf-8')
    data = json.loads(data)
    answer = data['answer']
    context = data['context']
    respuesta = generate_answer(answer, context)
    print(respuesta)
    return jsonify(respuesta)



@mod_api_project.route('/uploads/<id>/<id_project>', methods=['POST'])
def upload_file(id, id_project):
    if request.method == 'POST':
        f = request.files['file']
        respuesta = Upload_files(f, id, id_project)
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



#crear proyecto
@mod_api_project.route('/createprojects', methods=['POST'])
def create_Project():
    data = request.data.decode('utf-8')
    data = json.loads(data)
    data = create_new_project(data)
    return jsonify(data)

#eliminar proyecto
@mod_api_project.route('/deleteproject', methods=['POST'])
def delete_Project():
    data = request.data.decode('utf-8')
    data = json.loads(data)
    data = delete_project(data)
    return jsonify(data)


#obtener proyectos
@mod_api_project.route('/getprojects', methods=['POST'])
def get_projects():
    data = request.data.decode('utf-8')
    data = json.loads(data)
    data = get_projects_user(data)
    return jsonify(data)


#Obtener un proyecto
@mod_api_project.route('/getproject', methods=['POST'])
def get_project():
    data = request.data.decode('utf-8')
    data = json.loads(data)
    data = get_project_user(data)
    return jsonify(data)


#Archivos del proyecto
@mod_api_project.route('/getfiles', methods=['POST'])
def get_files():
    data = request.data.decode('utf-8')
    data = json.loads(data)
    data = get_files_project(data)
    return jsonify(data)


#texto del archivo
@mod_api_project.route('/getfile', methods=['POST'])
def get_file_text():
    data = request.data.decode('utf-8')
    data = json.loads(data)
    data = get_file_text_project(data)
    return jsonify(data)


#descargar archivo
@mod_api_project.route('/downloadfile/<id_project>/<id_file>/<id_user>', methods=['GET'])
def download_file(id_project, id_file, id_user):
    #data = request.data.decode('utf-8')
    #data = json.loads(data)
    data = download_file_project(id_project, id_file, id_user)
    #x = send_file(app.root_path.replace("\\","/") +'/' + data[0] +'/' + data[1], mimetype='application/octet-stream', download_name=data[1], as_attachment=True, attachment_filename=data[1])
    #x.headers["Access-Control-Allow-Origin"] = "*"
    #print(app.config['UPLOADS'], data[0]+data[1])
    #x = send_from_directory(data[0], data[1] , as_attachment=True)
    #retornar el archivo en binario
    print("aqui--------",data, type(data))
    return data
