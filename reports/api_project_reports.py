#pip install protobuf      ->    posiblemente instalar version 3.20.x o menor
#pip install pandas
import os
from ast import literal_eval
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, current_app
from flask import current_app
from werkzeug.security import generate_password_hash as genph
from werkzeug.security import check_password_hash as checkph
from models import *
from parrot import Parrot
import warnings
from werkzeug.utils import secure_filename
warnings.filterwarnings("ignore")
from deep_translator import GoogleTranslator
import PyPDF2
import secrets
from docx import Document
import zipfile

#Transformers
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelWithLMHead

tokenizer = AutoTokenizer.from_pretrained("b2bFiles")
model = AutoModelForSeq2SeqLM.from_pretrained("b2bFiles")

# To save it once you download it
#tokenizer = AutoTokenizer.from_pretrained("mrm8488/bert2bert-spanish-question-generation")
#model = AutoModelWithLMHead.from_pretrained("mrm8488/bert2bert-spanish-question-generation")

#tokenizer.save_pretrained("b2bFiles")
#model.save_pretrained("b2bFiles")

def prueba():
    # ...
    return {"test ":"prueba"}


def generate(texto1):
    texto  = literal_eval(texto1)['question']
    parrot = Parrot(model_tag="prithivida/parrot_paraphraser_on_T5")

    phrases = []
    translated = GoogleTranslator(source='spanish', target='english').translate(
        texto)
    phrases.append(translated)
    frases = []
    frases_bruto = []
    for phrase in phrases:
        print("-" * 100)
        print("Input_phrase: ", phrase)
        print("-" * 100)
        para_phrases = parrot.augment(input_phrase=phrase, use_gpu=False)
        for para_phrase in para_phrases:
            p = GoogleTranslator(source='english', target='spanish').translate(para_phrase[0])
            if p not in frases_bruto:
                frases_bruto.append(p)
                frases.append({"respuesta": p})
            print(p)
    return frases


def Upload_files(files, id, id_project):
    filename = secure_filename(files.filename)
    files.save(os.path.join(current_app.config['UPLOADS'], str(id)+"/"+str(id_project)+"/"+filename))
    extension = filename.split(".")[1]
    text = ""
    if extension == 'pdf':
        text = read_pdf(os.path.join(current_app.config['UPLOADS'], str(id)+"/"+str(id_project)+"/"+filename))
    elif extension == 'docx':
        text = read_docs(os.path.join(current_app.config['UPLOADS'], str(id)+"/"+str(id_project)+"/"+filename))

    return [{"message": "Archivo subido correctamente", "texto": str(text)}]


def read_pdf(file):
    pdfFileObj = open(file, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    texto = [""]
    for i in range(pdfReader.numPages):
        pageObj = pdfReader.getPage(i)
        texto[0] += pageObj.extractText() + "\n"
    return texto[0]


def read_docs(file):
    doc = Document(file)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return "\n".join(fullText)


def login_user(email, password):
    q = Users.query.filter_by(email=email).first()

    if q is not None:
        if checkph(q.password, password ):
            token = secrets.token_hex(16)
            q.token = token
            db.session.commit()
            hora_start = datetime.now()
            hora_finish = hora_start + timedelta(hours=1)
            token = secrets.token_hex()
            id = q.id
            to = Tokens(token=token, id_user=id, status_token='active', start_at=hora_start, finish_at=hora_finish)
            db.session.add(to)
            db.session.commit()
            return {"status": "200", "message": "Usuario logeado correctamente", "token": token, "id": id}
        else:
            return {"status": "500", "message": "Contraseña incorrecta"}
    else:
        return {'status':'500',"message": "Usuario o contraseña incorrectos"}


def register_user(data):
    name = data['name']
    email = data['email']
    lastname = data['lastname']
    hash_password = genph(data['password'])
    user = Users(
        name=data['name'],
        email=data['email'],
        password=hash_password,
        last_name=data['lastname'],
        created_at=datetime.now(),
        updated_at=None,
        role='user',
        deleted_at=None
    )
    db.session.add(user)
    db.session.commit()
    return {"status": "200", "message": "Usuario registrado correctamente"}


def generate_answer(answer, context, max_length=64):
    input_text = "answer: %s  context: %s </s>" % (answer, context)
    features = tokenizer([input_text], return_tensors='pt')

    output = model.generate(input_ids=features['input_ids'],
                                attention_mask=features['attention_mask'],
                                max_length=max_length)

    return {'status':200, 'message':tokenizer.decode(output[0])}


def create_new_project(data):
    name = data['name']
    description = data['description']
    id_user = data['id_user']
    project = Projects(
        name=name,
        description=description,
        id_user=id_user,
        dir = "", #"uploads/"+str(id_user)+"/"+name
        status="active",
        created_at=datetime.now(),
        updated_at=None,
        deleted_at=None

    )
    db.session.add(project)
    db.session.commit()
    #obtener el id del proyecto
    id_project = project.id
    #crear el directorio
    dir = "uploads/"+str(id_user)+"/"+str(id_project)
    os.makedirs(dir)
    #actualizar el proyecto con el directorio
    project.dir = dir
    db.session.commit()
    return {"status": "200", "message": "Proyecto creado correctamente", "id_project": id_project}


def get_projects_user(data):
    id_user = data['id_user']
    id_project = data['id_project']
    print(type(id_project), id_project)
    data = []
    #cuando el id del proyecto es -1 se devuelven todos los proyectos del usuario
    if id_project == -1:
        projects = Projects.query.filter_by(id_user=id_user).all()
        print(projects)
        for project in projects:
            data.append({
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "status": project.status,
                "created_at": project.created_at,
                "updated_at": project.updated_at,
                "deleted_at": project.deleted_at
            })
    #En caso contrario se devuelve el proyecto con el id especificado
    else:
        project = Projects.query.filter_by(id=id_project).filter_by(id_user=id_user).first()
        data.append({
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "status": project.status,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
            "deleted_at": project.deleted_at
        })
    return {"status": "200", "message": "Proyectos obtenidos correctamente", "projects": data}


def get_project_user(data):
    id_project = data['id_project']
    id_user = data['id_user']
    project = Projects.query.filter_by(id=id_project).filter_by(id_user=id_user).first()
    data = {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "status": project.status,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
        "deleted_at": project.deleted_at
    }
    return {"status": "200", "message": "Proyecto obtenido correctamente", "project": data}


def get_files_project(data):
    id_project = data['id_project']
    id_user = data['id_user']
    project = Projects.query.filter_by(id=id_project).filter_by(id_user=id_user).first()
    dir = project.dir
    files = os.listdir(dir)
    print(files)
    return {"status": "200", "message": "Archivos obtenidos correctamente", "files": files}