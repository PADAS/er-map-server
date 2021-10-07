import sys
import pathlib
import tempfile
import logging

from flask import Flask, jsonify, send_file, redirect
from flask_cors import CORS
from werkzeug.exceptions import NotFound
parent_path = pathlib.Path(__file__).parent
sys.path.append('/var/task/map-api/')
sys.path.append(parent_path)

import settings
import storage
from authentication import login_required, login_implementation

if not (settings.FRAMEWORK and settings.FRAMEWORK == 'Zappa'):
    logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


app = Flask(__name__)

resources=[
    {r"/api/v1.0/subjects": {"origins": ["http://localhost:3000", "https://ermap-sandbox.pamdas.org"]}},
    {r"/static": {"origins": ["http://localhost:3000", "https://ermap-sandbox.pamdas.org"]}}
]

cors = CORS(app, resources=resources)


def wrap_with_status(data):
  status = dict(data=data,
                status=dict(code=200, message="OK"))
  return status


@app.errorhandler(Exception)
def handle_error(error):
    message = [str(x) for x in error.args]
    description = None
    try:
        code = error.code
        description = error.description
    except AttributeError:
        code = 500
    response = dict(status=dict(
        code=code,
        message= description or message,
        type=error.__class__.__name__
    ))

    return jsonify(response), code

subject_storages = {}
def load_subject_storage(public_sites):
    for name, public_site in public_sites.items():
        subject_storages[name] = storage.get_storage(settings, public_site)

load_subject_storage(settings.PUBLIC_SITES)


@app.route('/', methods=['GET'])
def status():
    return jsonify(wrap_with_status({}))


@app.route('/api/v1.0/status', methods=['GET'])
def api_status():
    return jsonify(wrap_with_status({}))

@app.route('/<string:public_name>/api/v1.0/status', methods=['GET'])
def api_public_status(public_name):
    return jsonify(wrap_with_status({}))


@app.route('/oauth2/token/', methods=['POST'])
@login_implementation
def login():
    pass


#https://<>/api/v1.0/subjects?bbox=33.484954833984375,-2.5562194448989453,35.40893554687499,-1.5420196224821954
@app.route('/<string:public_name>/api/v1.0/subjects', methods=['GET'])
@login_required
def subjects(public_name):
    subjects = subject_storages[public_name].get_subjects()
    response = jsonify(wrap_with_status(subjects))
    response.headers.add('Access-Control-Allow-Origin', '*')
    #return jsonify(wrap_with_status(subjects))
    return response


#https://<>/api/v1.0/subject/3df5a521-f493-40df-a26e-ee70a0019300
@app.route('/<string:public_name>/api/v1.0/subject/<uuid:subject_id>',methods=['GET'])
@login_required
def subject(public_name, subject_id):
    subjects = subject_storages[public_name].get_subjects()
    subject_id = str(subject_id)
    try:
        subject = next(s for s in subjects['data'] if s['id'] == subject_id)
    except StopIteration:
        raise NotFound(f"Subject {subject_id}")

    response = jsonify(wrap_with_status(subject))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


#https://<>/api/v1.0/subject/3df5a521-f493-40df-a26e-ee70a0019300/tracks?since=2019-05-06
@app.route('/<string:public_name>/api/v1.0/subject/<string:subject_id>/tracks', methods=['GET'])
@login_required
def subject_tracks(public_name, subject_id):
    subject = subject_storages[public_name].get_subject(subject_id)
    response = jsonify(wrap_with_status(subject))
    response.headers["Access-Control-Allow-Origin"] = "*"
    #return jsonify(wrap_with_status(subject))
    return response

#https://<>/static/ranger-blue.svg
@app.route('/<string:public_name>/static/<string:image_name>', methods=['GET'])
def static_image(public_name, image_name):
    fh = tempfile.TemporaryFile('w+b')
    mimetype = subject_storages[public_name].get_static_image(fh, image_name)
    fh.seek(0)
    response = send_file(fh, mimetype=mimetype)
    response.headers["Access-Control-Allow-Origin"] = "*"
    #return send_file(fh, mimetype=mimetype)
    return response

@app.route('/<string:public_name>/media/<string:image_name>', methods=['GET'])
def static_media(public_name, image_name):
    url = subject_storages[public_name].get_static_image_redirect(image_name, "media")
    return redirect(url, code=302)

@app.route('/<string:public_name>/config/<string:name>', methods=['GET'])
def static_config(public_name, name):
    fh = tempfile.TemporaryFile('w+b')
    mimetype = subject_storages[public_name].get_static_image(fh, name, "config")
    fh.seek(0)
    return send_file(fh, mimetype=mimetype)

if __name__ == "__main__":
    app.run()
