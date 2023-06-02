# pip install protobuf      ->    posiblemente instalar version 3.20.x o menor
# pip install pandas
import json
import os
import math
import shutil
import uuid
from io import BytesIO
import time
import pandas as pd
from PyPDF2 import PdfReader
import fitz
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
# tokenizerQ = AutoTokenizer.from_pretrained("mrm8488/bert2bert-spanish-question-generation")
# modelQ = AutoModelWithLMHead.from_pretrained("mrm8488/bert2bert-spanish-question-generation")

# tokenizerQ.save_pretrained("b2bFiles")
# modelQ.save_pretrained("b2bFiles")


def prueba():
    # ...
    return {"test ": "prueba"}


def generate(texto1):
    texto = literal_eval(texto1)['question']
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
        para_phrases = parrot.augment(input_phrase=phrase, use_gpu=False, do_diverse=True)
        for para_phrase in para_phrases:
            p = GoogleTranslator(source='english', target='spanish').translate(para_phrase[0])
            if p not in frases_bruto:
                frases_bruto.append(p)
                frases.append({"respuesta": p})
            print(p)
    return frases


def upload_files(files, id, id_project):
    user = Usuario.query.get(id)
    project = Proyecto.query.get(id_project)

    if user is None or project is None:
        return [{"message": "Usuario o proyecto no encontrado"}]

    if project.usuario != user:
        return [{"message": "El proyecto no pertenece al usuario"}]

    filename = secure_filename(files.filename)
    new_filename = f"{id}_{id_project}_{filename}"

    files.save(os.path.join(current_app.config['UPLOADS'], new_filename))

    new_file_record = Archivo(
        project_id=id_project,
        filename=new_filename,
        original_filename=filename,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.session.add(new_file_record)
    db.session.commit()

    return [{"message": "Archivo subido correctamente", "filename": new_filename}]


def read_pdf(file):
    reader = PdfReader(file)
    number_of_pages = len(reader.pages)
    text = ""
    paragraphs = []
    for k in range(number_of_pages):
        page = reader.pages[k]
        # text += page.extract_text()

        paragraphs.append(page.extract_text(encoding='UTF-8').strip('\n'))
    return paragraphs


def read_docs(file):
    doc = Document(file)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return "\n".join(fullText)


def login_user(email, password):
    user = Usuario.query.filter_by(email=email).first()

    if user is None or not checkph(user.password, password):
        return {'status': '500', "message": "Usuario o contraseña incorrectos"}

    token = secrets.token_hex(16)  # Considera encriptar este token
    user.token = token
    db.session.commit()

    hora_start = datetime.utcnow()
    hora_finish = hora_start + timedelta(hours=1)
    token_encriptado = secrets.token_hex()  # Nuevamente, considera encriptar este token

    token_registro = Token(token=token_encriptado, user_id=user.user_id, status_token='active', start_at=hora_start, finish_at=hora_finish)
    db.session.add(token_registro)
    db.session.commit()

    return {"status": "200", "message": "Usuario logeado correctamente", "token": token_encriptado, "id": user.user_id}


def register_user(data):
    username = data['name']
    email = data['email']
    password = data['password']
    hash_password = genph(password)
    user = Usuario(
        username=username,
        email=email,
        password=hash_password,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.session.add(user)
    db.session.commit()
    return {"status": "200", "message": "Usuario registrado correctamente"}


def generate_answer(context: str, max_length: int = 512) -> str:
    inputText = "context: %s </s>" % (context)
    features = tokenizerQ([inputText], return_tensors='pt')

    output = modelQ.generate(input_ids=features['input_ids'],
                             attention_mask=features['attention_mask'],
                             max_length=max_length)

    question = tokenizerQ.decode(output[0]).strip("[SEP]")
    question = question.strip("CLS]")
    qa = pipeline("question-answering", model=modelA, tokenizer=tokenizerA)
    pred = qa(question=question, context=context)
    return {'status': 200,
            'message': 'ok',
            'question': question,
            'answer': pred['answer'],
            'score' : pred['score']
            }


def create_new_project(data):
    name = data['name']
    description = data['description']
    user_id = data['id_user']
    project = Proyecto(
        project_name=name,
        description=description,
        user_id=user_id,
        status="active",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    try:
        db.session.add(project)
        db.session.commit()
    except Exception as e:
        return {"status": "500", "message": str(e)}

    return {"status": "200", "message": "Proyecto creado correctamente", "project_id": project.project_id, 'name': name}


def get_projects_user(data):
    id_user = data['id_user']
    id_project = data['id_project']
    data = []
    # cuando el id del proyecto es -1 se devuelven todos los proyectos del usuario
    if id_project == -1:
        projects = Proyecto.query.filter_by(user_id=id_user).all()
        for project in projects:
            data.append({
                "id": project.project_id,
                "name": project.project_name,
                "description": project.description,
                "status": project.status,
                "created_at": project.created_at,
                "updated_at": project.updated_at,
            })
    # En caso contrario se devuelve el proyecto con el id especificado
    else:
        project = Proyecto.query.filter_by(project_id=id_project).filter_by(user_id=id_user).first()
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
    project = Proyecto.query.filter_by(project_id=id_project).filter_by(user_id=id_user).first()
    data = {
        "id": project.project_id,
        "name": project.project_name,
        "description": project.description,
        "status": project.status,
        "created_at": project.created_at,
        "updated_at": project.updated_at
    }
    return {"status": "200", "message": "Proyecto obtenido correctamente", "project": data}


def get_files_project(data):
    id_project = data['id_project']
    id_user = data['id_user']
    project = Proyecto.query.filter_by(project_id=id_project).filter_by(user_id=id_user).first()
    if project is None:
        return {"status": "500", "message": "No se encontró el proyecto"}
    id_proyecto = project.project_id
    archivos = Archivo.query.filter_by(project_id=id_proyecto).all()
    if archivos is None:
        return {"status": "500", "message": "No se encontraron archivos"}
    files = []
    for archivo in archivos:
        files.append({
            "id": archivo.file_id,
            "name": archivo.filename,
            "original_name": archivo.original_filename,
            "created_at": archivo.created_at,
            "updated_at": archivo.updated_at,
        })
    return {"status": "200", "message": "Archivos obtenidos correctamente", "files": files}


def get_meta_data_file_project(data):
    id_project = data['id_project']
    id_user = data['id_user']
    id_file_ = data['id_file']
    project = Proyecto.query.filter_by(project_id=id_project).filter_by(user_id=id_user).first()

    """dir = project.dir
    for file in os.listdir(dir):
        sep = file.split("-")
        id_proyecto = sep[0]
        id_file = sep[1]
        # quitar los primeros dos eleeentos del array
        sep.pop(0)
        sep.pop(0)
        # unir el array en un string
        name = "-".join(sep)
        if id_file == id_file_:
            file = dir + "/" + file
            with open(file, 'r') as f:
                data = {'name': name, 'size': os.path.getsize(file), 'type': 'file'}
            break"""
    return {"status": "200", "message": "Metadatos obtenidos correctamente", "meta_data": "data"}


def delete_project(data):
    id_project = data['id_project']
    id_user = data['id_user']
    project = Projects.query.filter_by(id=id_project).filter_by(id_user=id_user).first()
    # En caso de querer que el proyecto se lleve a la papelera o exista una papelera
    # project.status = "deleted"
    # project.deleted_at = datetime.now()
    # db.session.commit()

    # eliminar el directorio
    dir = project.dir
    shutil.rmtree(dir)

    # elimminar el proyecto
    db.session.delete(project)
    db.session.commit()

    return {"status": "200", "message": "Proyecto eliminado correctamente"}


def get_file_text_project(data, fun=False):
    id_project = data['id_project']
    id_user = data['id_user']
    id_file = data['id_file']  # Ahora esto es un array
    project = Proyecto.query.filter_by(project_id=id_project).filter_by(user_id=id_user).first()
    if project is None:
        return {"status": "500", "message": "No se encontró el proyecto"}
    else:
        files = Archivo.query.filter(Archivo.file_id.in_(id_file)).filter_by(project_id=id_project).all()
        if not files:
            return {"status": "500", "message": "No se encontraron los archivos"}
        else:
            result = []
            combined_text = []
            for file in files:
                extension = file.filename.split(".")[-1]
                text = ""
                if extension == 'pdf':
                    text = read_pdf("uploads/"+file.filename)
                elif extension == 'docx':
                    text = read_docs("uploads/"+file.filename)
                combined_text.append(text)
            result.append({"status": "200", "message": "Archivo obtenido correctamente", "text": combined_text, 'file': file,
                            'name': file.filename})

            if fun:
                return combined_text  # Aquí quizá querrás cambiar el comportamiento también

            return result
    return {"status": "200", "message": "Archivo no encontrado"}




def quiz_batchSec(par:list,cross:False,sections:64):
    questions=[]
    answers=[]
    predScore=[]
    start_id=0
    end_id=sections
    words=par.split()
    scale=math.trunc(len(words)/sections)
    if(cross):
       for i in range(scale):
        section_selected=' '.join(words[start_id:end_id])
        result = generate_answer(str(section_selected))
        questions.append(result['question'])
        answers.append(result['answer'])
        predScore.append(result['score'])
        if(i<scale):
          start_id=start_id+int(sections/2)
          end_id=start_id+sections
        if(i==scale):
          start_id=start_id+sections
          end_id=len(words)-(scale*i)
    if(not cross):
      for i in range(scale):
        section_selected=' '.join(words[start_id:end_id])
        result = generate_answer(str(section_selected))
        questions.append(result['question'])
        answers.append(result['answer'])
        predScore.append(result['score'])
        start_id=end_id
        if(i<scale):
          end_id=start_id+sections
        if(i==scale):
          end_id=len(words)-1
    return questions, answers, predScore


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

    dir = "temp"
    t = time.localtime()
    nhash = hash(str(t.tm_year) + str(t.tm_mon) + str(t.tm_mday) + str(t.tm_hour) + str(t.tm_min) + str(t.tm_sec))
    in_doc = f'{dir}/demo-{nhash}.docx'
    out_doc = f'{dir}/demo-{nhash}.pdf'
    name = f'demo-{nhash}.pdf'

    document.save(in_doc)
    doc = aw.Document(in_doc)
    doc.save(out_doc)
    return dir, name


def download_file_project(id_project, id_file, id_user):
    # id_project = data['id_project']
    # id_user = data['id_user']
    # id_file = data['id_file']
    project = Proyecto.query.filter_by(project_id=id_project).filter_by(user_id=id_user).first()
    if not project:
        return {"status": "400", "message": "Proyecto no encontrado"}
    else:
        file = Archivo.query.filter_by(file_id=id_file).first()
        if not file:
            return {"status": "400", "message": "Archivo no encontrado"}
        else:
            return send_from_directory("uploads", file.filename, as_attachment=True)

    """dir = project.dir
    f = []
    if not os.path.exists(dir):
        os.makedirs(dir)
    files = os.listdir(dir)
    for file in files:
        sep = file.split("-")
        id_proyecto = sep[0]
        id_file_ = sep[1]
        # quitar los primeros dos eleeentos del array
        sep.pop(0)
        sep.pop(0)
        # unir el array en un string
        name = "-".join(sep)
        if id_file == id_file_:
            # retornar el archivo para descargar"""

    return {"status": "200", "message": "Archivo no encontrado"}


def download_file_project_tmp(name, id_user):
    f = name.split("/")
    namef = f[1]
    dir = f[0]

    return send_from_directory(dir, namef, as_attachment=True)


def descargar_archivo(dir, nombre_archivo):
    # Obtener la ruta completa del archivo
    ruta_archivo = os.path.join(dir, nombre_archivo)

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
        # quitar los primeros dos eleeentos del array
        sep.pop(0)
        sep.pop(0)
        # unir el array en un string
        name = "-".join(sep)
        if id_file == id_file_:
            # retornar el arcxhivo para descargar
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
    # gneerar un hash para el nombre del archivo

def topQuestions(question:list, answer:list, score:list, top:int):
    df = pd.DataFrame(columns=['question', 'answer', 'score'])
    for i in range(len(question)):
        newData={'question':question[i], 'answer':answer[i], 'score':score[i]}
        df = df.append(newData, ignore_index=True)
    df = df.sort_values(by=['score'], ascending=False)
    df = df.head(top)
    questions=df['question'].tolist()
    aswers=df['answer'].tolist()
    return questions, aswers
def createQuiz(data, id, id_file, id_proyecto):
    texto = get_file_text_project(data, fun=True)
    texto_unido = ' '.join([' '.join(pagina) for pagina in texto])
    q, a, score = quiz_batchSec(texto_unido, False, 128)
    topQ,topA=topQuestions(q, a, score, 10)
    name, dir = document_to_quiz(topQ, topA)
    saveFileInDb(id_proyecto, [topQ, topA])
    # createPDF()
    # return {"status": "400", "message": "Error al crear el quiz"}
    return {"status": "200", "message": "Quiz creado correctamente", "quiz questions": topQ,
            "quiz answers": topA}


def saveFileInDb(id_proyecto, data):
    newTest = Test(proyecto_id=id_proyecto, test_data=json.dumps({"questions": data[0], "answers": data[1]}))
    db.session.add(newTest)
    db.session.commit()

def generate_pdf(data):
    questions = data.get('q', [])
    answers = data.get('a', [])
    directorio, name = document_to_quiz(questions, answers)
    return send_from_directory(directorio, name, as_attachment=True)


def borrar_archivos(directorio):
    for filename in os.listdir(directorio):
        file_path = os.path.join(directorio, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                os.rmdir(file_path)
        except Exception as e:
            print('Error al borrar %s. Razón: %s' % (file_path, e))


def get_all_quiz(data):
    id_proyecto = data['id_project']
    id_user = data['id_user']
    id_file = data['id_file']

    project = Test.query.filter_by(proyecto_id=id_proyecto).all()
    if project:
        data_n = []
        for p in project:
            try:
                data_n.append({'cuestionario':json.loads(p.test_data), 'fecha':p.created_at.strftime("%d/%m/%Y %H:%M:%S")})
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")
        return {"status": "200", "message": "Quiz encontrado", "quiz": data_n}
    return {"status": "200", "message": "Quiz no encontrado"}



