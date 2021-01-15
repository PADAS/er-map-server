import logging
import hashlib

from functools import wraps
from flask import g, request, redirect, url_for, jsonify
from werkzeug.exceptions import Unauthorized, BadRequest

import settings
import storage

logger = logging.getLogger(__name__)
credential_storage = storage.EAPStorage(settings.SUBJECTS_BUCKET, settings.AWS_REGION)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        authorization = request.headers.get("authorization")
        if authorization and authorization.startswith('Bearer '):
            token = authorization[len('Bearer '):]
            if token == settings.LOGIN_TOKEN:
                return f(*args, **kwargs)
        raise Unauthorized()
    return decorated_function


def login_implementation(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = request.form['username']
        password = request.form['password']
        grant_type = request.form['grant_type']

        if not username or not password:
            raise BadRequest('Specify username or password')

        if grant_type != 'password':
            raise BadRequest('Invalid grant_type')

        try:
            user = credential_storage.get_user_credentials(username.lower())
        except Exception as ex:
            logger.info(f"User not found: {username}, {ex}")
            raise Unauthorized()

        if not user:
            logger.info(f"User not found: {username}")
            raise Unauthorized()

        password_hash = hashlib.md5(password.encode("utf-8"))
        if password_hash.hexdigest() != user['pw5']:
            logger.info(f"User {username} password does not match")
            raise Unauthorized()

        return jsonify(dict(access_token=settings.LOGIN_TOKEN))

    return decorated_function