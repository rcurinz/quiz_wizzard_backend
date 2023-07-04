import json
from flask import (Blueprint, jsonify, request)
from flask_cors import CORS
from werkzeug.utils import secure_filename

from app import app
from reports.api_project_reports import *

cors = CORS(app)
mod_api_project = Blueprint('api_project', __name__, template_folder='templates', url_prefix='/api')


@mod_api_project.route('/')
def hello_world():  # put application's code here
    return {'data': "Hello World!"}
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
        respuesta = upload_files(f, id, id_project)
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
    print(data)
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


@mod_api_project.route('/get-meta-data-file', methods=['POST'])
def get_meta_data_file():
    data = request.data.decode('utf-8')
    data = json.loads(data)
    data = get_meta_data_file_project(data)
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
    #print("aqui--------",data, type(data))
    return data

@mod_api_project.route('/has-test-associated/<id_project>/<id_file>', methods=['GET'])
def has_test_associated(id_project, id_file):
    print(id_project, id_file)
    file = Archivo.query.filter_by(file_id=id_file).first()
    if not file:
        return {"status": "400", "message": "Archivo no encontrado"}, 400

    associated_test_id = None

    for test in file.tests:
        if test.proyecto_id == int(id_project) and not test.is_multi_file:
            associated_test_id = test.test_id
            break

    if associated_test_id:
        return {"test_id": associated_test_id}
    else:
        return {"status": "404", "test_id": None}, 404

@mod_api_project.route('/downloadfiletemp', methods=['POST'])
def download_file_temp():
    data = request.data.decode('utf-8')
    data = json.loads(data)
    id_file = data['id_file']
    id_user = data['id_user']
    data = download_file_project_tmp( id_file, id_user)
    return data



#leer archivo
@mod_api_project.route('/createquiz', methods=['POST'])
def createquiz():
    data = request.get_json()
    id_proyecto = data['id_project']
    id_file = data['id_file']
    id = data['id_user']
    cantidad = data['cant_questions']
    reescribir = data['reescribir']
    p_inicio = data['p_inicio']
    p_final = data['p_final']
    data = createQuiz(data, id, id_file, id_proyecto, cantidad, reescribir, p_inicio, p_final)
    return jsonify(data)


#Generar pdf
@mod_api_project.route('/generatepdf', methods=['POST'])
def generatepdf():
    data = request.data.decode('utf-8')
    data = json.loads(data)
    file = generate_pdf(data)
    borrar_archivos("temp")
    return file


#get cuesitonarios generados
@mod_api_project.route('/getquizgenerated', methods=['POST'])
def getallquiz():
    data = request.get_json()
    data = get_all_quiz(data)
    return jsonify(data)

#delete file
@mod_api_project.route('/deletefilebyid', methods=['POST'])
def deletefile():
    data = request.get_json()
    data = delete_file(data)
    return jsonify(data)


#cuestionario by id
@mod_api_project.route('/get-cuestionario-by-id/<id>', methods=['GET'])
def getquizbyid(id):
    data = get_quiz_by_id(id)
    response = jsonify(data)
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response