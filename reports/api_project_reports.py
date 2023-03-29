# pip install protobuf      ->    posiblemente instalar version 3.20.x o menor
# pip install pandas

import os
import math
import shutil
from io import BytesIO
import time
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
from fpdf import FPDF
# Transformers
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelWithLMHead
warnings.filterwarnings("ignore")
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
from docx2pdf import convert
import pythoncom
import aspose.words as aw
# To load the model and tokenizer
modelA = AutoModelForQuestionAnswering.from_pretrained("MarcBrun/ixambert-finetuned-squad-eu-en")
tokenizerA = AutoTokenizer.from_pretrained("MarcBrun/ixambert-finetuned-squad-eu-en")

tokenizerQ = AutoTokenizer.from_pretrained("b2bFiles")
modelQ = AutoModelForSeq2SeqLM.from_pretrained("b2bFiles")

# To save it once you download it
#tokenizerQ = AutoTokenizer.from_pretrained("mrm8488/bert2bert-spanish-question-generation")
#modelQ = AutoModelWithLMHead.from_pretrained("mrm8488/bert2bert-spanish-question-generation")

#tokenizerQ.save_pretrained("b2bFiles")
#modelQ.save_pretrained("b2bFiles")


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
    paragraphs=[]
    for k in range(number_of_pages):
        page = reader.pages[k]
        #text += page.extract_text()

        paragraphs.append(page.extract_text().strip('\n'))
    """pdfFileObj = open(file, 'rb')
    pdfReader = PyPDF2.PdfReader(pdfFileObj)
    
    for i in range(pdfReader.pages):
        pageObj = pdfReader.getPage(i)
        print(pageObj.extractText())
        texto[0] += pageObj.extractText() + "\n"
    pdfFileObj.close()"""
    return paragraphs


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


def generate_answer(context:str, max_length:int=2048)->str:
  inputText = "context: %s </s>" % ( context)
  features = tokenizerQ([inputText], return_tensors='pt')

  output = modelQ.generate(input_ids=features['input_ids'], 
               attention_mask=features['attention_mask'],
               max_length=max_length)

  question=tokenizerQ.decode(output[0]).strip("[SEP]")
  question =question.strip("CLS]") 
  qa = pipeline("question-answering", model=modelA, tokenizer=tokenizerA)
  pred = qa(question=question,context=context)
  return {'status': 200,
            'message': 'ok',
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

def quiz_batch(paragraphs:list)->list:
  questions=[]
  answers=[]
  for par in paragraphs:
    result = generate_answer(par[0:512])
    questions.append(result['question'])
    answers.append(result['answer'])
  return questions,answers


def quiz_batchSec(par:list,cross:bool,sections:int)->list:
    if(sections>216):
      raise  ValueError("Sections mus not exceed 216 words")
    questions=[]
    answers=[]
    start_id=0
    end_id=sections
    words=par.split()
    scale=math.trunc(len(words)/sections)
    if(cross):
      for i in range(scale):
        section_selected=' '.join(str(words[e])for e in range(start_id,end_id))
        result = generate_answer(str(section_selected),sections)
        questions.append(result['question'])
        answers.append(result['answer'])
        if(i<scale):
          start_id=end_id-int((end_id/2))
          end_id=sections*(i+2)-int(end_id/2)
        if(i==scale):
          start_id=end_id
          end_id=len(words)-(scale*i)
    if(not cross):
      for i in range(scale):
        section_selected=' '.join(str(words[e])for e in range(start_id,end_id))
        result = generate_answer(str(section_selected),sections)
        questions.append(result['question'])
        answers.append(result['answer'])
        if(i<scale):
          start_id=end_id
          end_id=sections*(i+2)
        if(i==scale):
          start_id=end_id
          end_id=len(words)-(scale*i)

    return questions,answers

def document_to_quiz(q: list, a: list) -> object:
    document = Document()

    document.add_heading('Exámen Generado', 0)

    p = document.add_paragraph('Tu examen generado es el siguiente:').bold = True
    document.add_paragraph('Tus preguntas son', style='List Bullet')
    table = document.add_table(rows=1, cols=3)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Pregunta'
    hdr_cells[1].text = 'Respuesta'

    for i in range(len(q)):
        row_cells = table.add_row().cells
        row_cells[0].text = str(q[i])
        row_cells[1].text = str(a[i])


    t=time.localtime()
    nhash=hash(str(t.tm_year)+str(t.tm_mon)+str(t.tm_mday)+str(t.tm_hour)+str(t.tm_min)+str(t.tm_sec))
    in_doc=f'temp/demo{nhash}.docx'
    out_doc=f'temp/demo{nhash}.pdf'

    document.save(in_doc)
    doc = aw.Document(in_doc)
    doc.save(out_doc)
    return out_doc


   

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


def download_file_project_tmp(name, id_user):
    f = name.split("/")
    namef = f[1]
    dir = f[0]

    return send_from_directory(dir, namef, as_attachment=True)

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


def createPDF():
    pdf = FPDF()

    # Añadimos una página al PDF
    pdf.add_page()

    # Definimos la fuente y el tamaño para el título
    pdf.set_font("Arial", size=24, style="B")
    pdf.cell(0, 20, txt="Examen generado", ln=1, align="C")

    # Definimos la fuente y el tamaño para las preguntas y respuestas
    pdf.set_font("Arial", size=16)
    pdf.set_text_color(0, 0, 255)

    # Definimos el color de fondo para las preguntas y respuestas
    pdf.set_fill_color(220, 220, 220)

    # Creamos una lista de preguntas y respuestas
    preguntas_respuestas = [
        {
            "pregunta": "¿Cuál es la capital de Francia?",
            "respuesta": "París"
        },
        {
            "pregunta": "¿En qué año se fundó Apple?",
            "respuesta": "1976"
        },
        {
            "pregunta": "¿Cuál es el río más largo del mundo?",
            "respuesta": "El río Amazonas"
        }
    ]

    # Recorremos la lista de preguntas y respuestas y las escribimos en el PDF
    for i, pregunta_respuesta in enumerate(preguntas_respuestas):
        pregunta = pregunta_respuesta["pregunta"]
        respuesta = pregunta_respuesta["respuesta"]
        pdf.cell(0, 10, txt=f"{i + 1}. {pregunta}\n", fill=True)
        pdf.cell(0, 10, txt=f"Respuesta: {respuesta}", ln=1)
    # Guardamos el PDF
    pdf.output("temp/examen.pdf")


def createQuiz(data):
    texto = get_file_text_project(data, fun=True)
    #q,a = quiz_batch(texto)
    q,a = quiz_batchSec(texto[0],False,128)
    name = document_to_quiz(q,a)
    createPDF()
    #return {"status": "400", "message": "Error al crear el quiz"}
    return {"status": "200", "message": "Quiz creado correctamente","name": name ,"quiz questions": q,"quiz answers": a}