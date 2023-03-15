# pip install protobuf      ->    posiblemente instalar version 3.20.x o menor
# pip install pandas

import os
import shutil
from io import BytesIO

from PyPDF2 import PdfReader
import secrets
from ast import literal_eval
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, current_app, send_from_directory
from flask import current_app, send_file
from werkzeug.security import generate_password_hash as genph
from werkzeug.security import check_password_hash as checkph
from models import *
from parrot import Parrot
import warnings
from werkzeug.utils import secure_filename
from deep_translator import GoogleTranslator
from docx import Document
# Transformers
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelWithLMHead
warnings.filterwarnings("ignore")
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
# To load the model and tokenizer
modelQ = AutoModelForQuestionAnswering.from_pretrained("MarcBrun/ixambert-finetuned-squad-eu-en")
tokenizer = AutoTokenizer.from_pretrained("MarcBrun/ixambert-finetuned-squad-eu-en")

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
        para_phrases = parrot.augment(input_phrase=phrase, use_gpu=False, do_diverse = True)
        for para_phrase in para_phrases:
            p = GoogleTranslator(source='english', target='spanish').translate(para_phrase[0])
            if p not in frases_bruto:
                frases_bruto.append(p)
                frases.append({"respuesta": p})
            print(p)
    return frases


def Upload_files(files, id, id_project):
    print( id, id_project)
    project = Projects.query.filter_by(id=id_project).filter_by(id_user=id).first()
    dir = project.dir
    cant = len(os.listdir(dir))
    filename = str(id_project)+"-"+str(cant)+"-"+secure_filename(files.filename)
    files.save(os.path.join(current_app.config['UPLOADS'], str(id)+"/"+str(id_project)+"/"+filename))
    extension = filename.split(".")[1]
    text = ""
    if extension == 'pdf':
        text = read_pdf(os.path.join(current_app.config['UPLOADS'], str(id)+"/"+str(id_project)+"/"+filename))
    elif extension == 'docx':
        text = read_docs(os.path.join(current_app.config['UPLOADS'], str(id)+"/"+str(id_project)+"/"+filename))

    return [{"message": "Archivo subido correctamente", "texto": str(text)}]


def read_pdf(file):

    reader = PdfReader(file)
    number_of_pages = len(reader.pages)
    text = ""
    for k in range(number_of_pages):
        page = reader.pages[k]
        text += page.extract_text()


    """pdfFileObj = open(file, 'rb')
    pdfReader = PyPDF2.PdfReader(pdfFileObj)
    
    for i in range(pdfReader.pages):
        pageObj = pdfReader.getPage(i)
        print(pageObj.extractText())
        texto[0] += pageObj.extractText() + "\n"
    pdfFileObj.close()"""
    return text


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


def generate_answer(context:str,max_lenght=256):
    inputText = "context: %s </s>" % ( context)
    features = tokenizer([inputText], return_tensors='pt')
    output = model.generate(input_ids = features['input_ids'],
                            attention_mask= features['attention_mask'],
                            max_lenght=max_lenght)

    text=tokenizer.decode(output[0]).strip("[SEP]")
    question = text.strip("CLS]")

    qa = pipeline("question-answering", model=modelQ, tokenizer=modelQ)
    pred = qa(question=question,context=context)
    return {'status': 200,
            'message': text,
            'question': question,
            'answer': pred['answer']
            }


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
    return {"status": "200", "message": "Proyecto creado correctamente", "id_project": id_project, 'name': name}


def get_projects_user(data):
    id_user = data['id_user']
    id_project = data['id_project']
    data = []
    #cuando el id del proyecto es -1 se devuelven todos los proyectos del usuario
    if id_project == -1:
        projects = Projects.query.filter_by(id_user=id_user).all()
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
    print(data)
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
    f = []
    if not os.path.exists(dir):
        os.makedirs(dir)
    files = os.listdir(dir)
    for file in files:
        sep = file.split("-")
        id_proyecto = sep[0]
        id_file = sep[1]
        #quitar los primeros dos eleeentos del array
        sep.pop(0)
        sep.pop(0)
        #unir el array en un string
        name = "-".join(sep)
        f.append({'id_proyecto': id_proyecto, 'id_file': id_file, 'name': name, 'extension': file.split(".")[-1]})

    return {"status": "200", "message": "Archivos obtenidos correctamente", "files": f}

def get_meta_data_file_project(data):
    id_project = data['id_project']
    id_user = data['id_user']
    id_file_ = data['id_file']
    project = Projects.query.filter_by(id=id_project).filter_by(id_user=id_user).first()
    dir = project.dir
    for file in os.listdir(dir):
        sep = file.split("-")
        id_proyecto = sep[0]
        id_file = sep[1]
        #quitar los primeros dos eleeentos del array
        sep.pop(0)
        sep.pop(0)
        #unir el array en un string
        name = "-".join(sep)
        if id_file == id_file_:
            file = dir+"/"+file
            with open(file, 'r') as f:
                data = {'name': name, 'size': os.path.getsize(file), 'type': 'file'}
            break
    return {"status": "200", "message": "Metadatos obtenidos correctamente", "meta_data": data}



def delete_project(data):
    id_project = data['id_project']
    id_user = data['id_user']
    project = Projects.query.filter_by(id=id_project).filter_by(id_user=id_user).first()
    # En caso de querer que el proyecto se lleve a la papelera o exista una papelera
    # project.status = "deleted"
    # project.deleted_at = datetime.now()
    # db.session.commit()

    #eliminar el directorio
    dir = project.dir
    shutil.rmtree(dir)

    #elimminar el proyecto
    db.session.delete(project)
    db.session.commit()

    return {"status": "200", "message": "Proyecto eliminado correctamente"}


def get_file_text_project(data, fun=False):
    id_project = data['id_project']
    id_user = data['id_user']
    id_file = data['id_file']
    project = Projects.query.filter_by(id=id_project).filter_by(id_user=id_user).first()
    dir = project.dir
    f = []
    if not os.path.exists(dir):
        os.makedirs(dir)
    files = os.listdir(dir)
    for file in files:
        sep = file.split("-")
        id_proyecto = sep[0]
        id_file_ = sep[1]
        #quitar los primeros dos eleeentos del array
        sep.pop(0)
        sep.pop(0)
        #unir el array en un string
        name = "-".join(sep)
        if id_file == id_file_:
            extension = file.split(".")[-1]
            text = ""
            if extension == 'pdf':
                text = read_pdf(dir +"/" +file)
            elif extension == 'docx':
                text = read_docs(dir +"/" +file)
            #retornar el arcxhivo
            if fun:
                return text
            return {"status": "200", "message": "Archivo obtenido correctamente", "text": text, 'file':file, 'name':name}
    return {"status": "200", "message": "Archivo no encontrado"}


def download_file_project(id_project, id_file, id_user):
    #id_project = data['id_project']
    #id_user = data['id_user']
    #id_file = data['id_file']
    project = Projects.query.filter_by(id=id_project).filter_by(id_user=id_user).first()
    dir = project.dir
    f = []
    if not os.path.exists(dir):
        os.makedirs(dir)
    files = os.listdir(dir)
    for file in files:
        sep = file.split("-")
        id_proyecto = sep[0]
        id_file_ = sep[1]
        #quitar los primeros dos eleeentos del array
        sep.pop(0)
        sep.pop(0)
        #unir el array en un string
        name = "-".join(sep)
        if id_file == id_file_:
            #retornar el arcxhivo para descargar
            return send_from_directory(dir, file, as_attachment=True)
    return {"status": "200", "message": "Archivo no encontrado"}


def descargar_archivo(dir, nombre_archivo):
    # Obtener la ruta completa del archivo
    ruta_archivo = os.path.join(dir, nombre_archivo)
    print(ruta_archivo, dir)

    # Verificar si el archivo existe
    if not os.path.exists(ruta_archivo):
        # Si no existe, devolver un mensaje de error
        return "El archivo no existe", 404

    # Si el archivo existe, leerlo y devolverlo en la respuesta
    with open(ruta_archivo, 'rb') as f:
        contenido = f.read()
    return send_file(
        BytesIO(contenido),
        mimetype='application/octet-stream'
    )



def read_file_project(data):
    id_project = data['id_project']
    id_user = data['id_user']
    id_file = data['id_file']
    project = Projects.query.filter_by(id=id_project).filter_by(id_user=id_user).first()
    dir = project.dir
    f = []
    if not os.path.exists(dir):
        os.makedirs(dir)
    files = os.listdir(dir)
    for file in files:
        sep = file.split("-")
        id_proyecto = sep[0]
        id_file_ = sep[1]
        #quitar los primeros dos eleeentos del array
        sep.pop(0)
        sep.pop(0)
        #unir el array en un string
        name = "-".join(sep)
        if id_file == id_file_:
            #retornar el arcxhivo para descargar
            return send_from_directory(dir, file, as_attachment=False)
    return {"status": "200", "message": "Archivo no encontrado"}



def createQuiz(data):
    texto = get_file_text_project(data, fun=True)
    t = "El sol brillaba en el cielo y las hojas de los árboles se mecían suavemente con la brisa. El ambiente era tranquilo y apacible, como si el mundo hubiera entrado en un estado de calma perfecta. Los pájaros cantaban alegremente y la hierba era de un verde intenso y exuberante. En ese momento, todo parecía posible, todo parecía alcanzable. La mente podía divagar libremente y soñar con cualquier cosa que se deseara. Era un momento mágico, un momento de paz y felicidad que parecía durar eternamente. Y así fue, durante un tiempo que se sentía infinito. Pero como todo en la vida, llegó el momento de seguir adelante, de avanzar hacia nuevos horizontes y explorar todo lo que el mundo tenía por ofrecer. Y así, la mente se puso en marcha, preparada para lo que vendría a continuación."

    text = "El Mundial de Fútbol de 1998, celebrado en Francia, fue uno de los eventos más importantes en la historia del deporte. La selección francesa, liderada por el legendario Zinedine Zidane, consiguió su primera Copa del Mundo tras vencer a Brasil en la final por 3-0.erra o la apasionada celebración de los jugadores franceses en el estadio Saint-Denis después de ganar el título."
    r = generate_answer(text)

    #return {"status": "400", "message": "Error al crear el quiz"}
    return {"status": "200", "message": "Quiz creado correctamente", "quiz": r}