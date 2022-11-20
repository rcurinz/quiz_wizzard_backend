import json
from flask import (Blueprint, jsonify, request)
from flask_cors import CORS
from app import app
from reports.api_project_reports import *

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
mod_api_project = Blueprint('api_project', __name__, template_folder='templates', url_prefix='/api/v1/projects')



#test
@mod_api_project.route('/test')
def test():
    data = prueba()
    return jsonify(data)