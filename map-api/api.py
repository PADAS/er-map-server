import sys
import pathlib
import tempfile
import logging

from flask import Flask, jsonify, send_file, redirect
import settings
import storage
from authentication import login_required, login_implementation

if not (settings.FRAMEWORK and settings.FRAMEWORK == 'Zappa'):
    logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
parent_path = pathlib.Path(__file__).parent
logger.info(f'api.py parent path {parent_path}')
sys.path.append('/var/task/map-api/')
sys.path.append(parent_path)


app = Flask(__name__)
#app.config['CORS_HEADERS'] = 'Content-Type'

#cors = CORS(app, resources={r"/api/v1.0/subjects": {"origins": "http://localhost:3000"}})


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

subject_storage = storage.get_storage(settings)


@app.route('/', methods=['GET'])
def status():
    return jsonify(wrap_with_status({}))


@app.route('/api/v1.0/status', methods=['GET'])
def api_status():
    return jsonify(wrap_with_status({}))


@app.route('/oauth2/token/', methods=['POST'])
@login_implementation
def login():
    pass


#https://<>/api/v1.0/subjects?bbox=33.484954833984375,-2.5562194448989453,35.40893554687499,-1.5420196224821954
@app.route('/api/v1.0/subjects', methods=['GET'])
#@cross_origin(origin='localhost',headers=['Content- Type', 'Authorization'])
@login_required
def subjects():
    subjects = subject_storage.get_subjects()
    response = jsonify(wrap_with_status(subjects))
    response.headers.add('Access-Control-Allow-Origin', '*')
    #response.headers["Access-Control-Allow-Origin"] = "*"
    #return jsonify(wrap_with_status(subjects))
    return response


#https://<>/api/v1.0/subject/3df5a521-f493-40df-a26e-ee70a0019300/tracks?since=2019-05-06
@app.route('/api/v1.0/subject/<uuid:subject_id>',methods=['GET'])
@login_required
def subject():
    raise NotImplementedError()


#https://<>/api/v1.0/subject/3df5a521-f493-40df-a26e-ee70a0019300/tracks?since=2019-05-06
@app.route('/api/v1.0/subject/<string:subject_id>/tracks', methods=['GET'])
@login_required
def subject_tracks(subject_id):
    subject = subject_storage.get_subject(subject_id)
    response = jsonify(wrap_with_status(subject))
    response.headers["Access-Control-Allow-Origin"] = "*"
    #return jsonify(wrap_with_status(subject))
    return response

#https://<>/static/ranger-blue.svg
@app.route('/static/<string:image_name>', methods=['GET'])
def static_image(image_name):
    fh = tempfile.TemporaryFile('w+b')
    mimetype = subject_storage.get_static_image(fh, image_name)
    fh.seek(0)
    response = send_file(fh, mimetype=mimetype)
    response.headers["Access-Control-Allow-Origin"] = "*"
    #return send_file(fh, mimetype=mimetype)
    return response

@app.route('/media/<string:image_name>', methods=['GET'])
def static_media(image_name):
    url = subject_storage.get_static_image_redirect(image_name, "media")
    return redirect(url, code=302)

@app.route('/config/<string:name>', methods=['GET'])
def static_config(name):
    fh = tempfile.TemporaryFile('w+b')
    mimetype = subject_storage.get_static_image(fh, name, "config")
    fh.seek(0)
    return send_file(fh, mimetype=mimetype)



#ICON <optional, since I will hardcode these for the demo>
#https://<>/static/elephant-black-male.svg

if __name__ == "__main__":
    app.run()
