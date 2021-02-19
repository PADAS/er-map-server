import logging
import json
import tempfile
import mimetypes
import urllib.request
import os
from pathlib import Path

import boto3


logger = logging.getLogger(__name__)


def get_storage(settings):
    if getattr(settings, "SUBJECTS_BUCKET", None):
        return S3Storage(getattr(settings, "SUBJECTS_BUCKET"), getattr(settings, "AWS_REGION"))
    elif getattr(settings, "SUBJECTS_FOLDER", None):
        return LocalStorage(getattr(settings, "SUBJECTS_FOLDER"))
    raise NotImplementedError("No storage type found")


class LocalStorage:
    def __init__(self, root_folder):
        self.root_folder = Path(root_folder)
        self.subjects_dir = self.root_folder / 'subjects'
        self.static_dir = self.root_folder / 'static'

        self.subjects_dir.mkdir(parents=True, exist_ok=True)
        self.static_dir.mkdir(parents=True, exist_ok=True)

    def save_obj_to_file(self, path, obj):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w+b') as fh:
            s_obj = json.dumps(obj)
            fh.write(s_obj.encode('utf-8'))

    def get_obj_from_file(path, fh):
        with open(path, "rb") as source_fh:
            fh.write(source_fh.read())

    """
    PUBLIC INTERFACE
    """
    def get_subjects(self):
        path = self.subjects_dir / "subjects.json"
        with open(path,  "rb") as fh:
            return json.loads(fh.read().decode())

    def get_subject(self, subject_id):
        path = self.subjects_dir / subject_id / "tracks.json"
        with open(path,  "rb") as fh:
            return json.loads(fh.read().decode())

    def save_subjects(self, subjects):
        path = self.subjects_dir / "subjects.json"
        self.save_obj_to_file(path, subjects)

    def save_subject_track(self, subject, track):
        path = self.subjects_dir / subject["id"] / "tracks.json"
        self.save_obj_to_file(path, track)

    def save_subject_image(self, subject):
        #png_file = subject["image_url"].replace(".svg", ".png")
        path = Path(os.path.dirname(self.subjects_dir) + "/" + subject["image_url"]) #to save as svg
        #path = Path(os.path.dirname(self.subjects_dir) + "/" + png_file)

        # makes a directory and saves svg image if not already been saved before
        if not os.path.exists(path) :
            svg_url = subject["image_url"].replace(".png", ".svg")
            url = "https://sandbox.pamdas.org" + svg_url
            #url = "https://sandbox.pamdas.org" + subject["image_url"]
            response = urllib.request.urlopen(url)
            urllib.request.urlretrieve(url, path)

    def get_static_image(self, fh, image_name, folder=None):
        if not folder:
            folder = self.static_dir
        mimetype = mimetypes.guess_type(image_name)[0]

        #png_image_name = image_name.replace(".svg", ".png")
        path = folder / image_name # to get as an svg file
        #path = folder / png_image_name

        # here we need to load the image file into the fh
        with open(path, "rb") as source_fh:
            fh.write(source_fh.read())
        return mimetype

    def get_static_image_redirect(self, image_name, folder=None):
        raise NotImplementedError()

class S3Storage:
    def __init__(self, bucket, region):
        self.bucket_name = bucket
        self.subjects_dir = 'subjects'
        self.static_dir = 'static'
        self.users_dir = 'users'

        self.session = boto3.Session(region_name=region)
        self.s3_session = self.session.resource('s3')
        self.bucket = self.s3_session.Bucket(bucket)
        self.client = self.session.client('s3')

    def upload_file(self, source_file, dest_key):
        logger.debug('Uploading to bucket %s path %s',
                     self.bucket.name, dest_key)
        return self.bucket.upload_fileobj(source_file, dest_key)

    def download_file(self, source_key, dest_file):
        return self.bucket.download_fileobj(source_key, dest_file)

    def save_obj_to_file(self, path, obj):
        with tempfile.TemporaryFile('w+b') as fh:
            s_obj = json.dumps(obj)
            fh.write(s_obj.encode('utf-8'))
            fh.seek(0)
            self.upload_file(fh, path)

    """
    PUBLIC INTERFACE
    """
    def get_subjects(self):
        path = f'{self.subjects_dir}/subjects.json'
        with tempfile.TemporaryFile('w+b') as fh:
            self.download_file(path, fh)
            fh.seek(0)
            return json.loads(fh.read().decode())

    def get_subject(self, subject_id):
        path = f'{self.subjects_dir}/{subject_id}/tracks.json'
        with tempfile.TemporaryFile('w+b') as fh:
            self.download_file(path, fh)
            fh.seek(0)
            return json.loads(fh.read().decode())

    def save_subjects(self, subjects):
        subjects_path = f'{self.subjects_dir}/subjects.json'
        self.save_obj_to_file(subjects_path, subjects)

    def save_subject_track(self, subject, track):
        track_path = f'{self.subjects_dir}/{subject["id"]}/tracks.json'
        self.save_obj_to_file(track_path, track)

    def get_static_image(self, fh, image_name, folder=None):
        if not folder:
            folder = self.static_dir
        mimetype = mimetypes.guess_type(image_name)[0]

        path = f'{folder}/{image_name}'
        self.bucket.download_fileobj(path, fh)
        return mimetype

    def get_static_image_redirect(self, image_name, folder=None):
        if not folder:
            folder = self.static_dir

        path = f'{folder}/{image_name}'
        url = self.client.generate_presigned_url('get_object',
             Params = {'Bucket': self.bucket_name, 'Key': path},
                    ExpiresIn = 100)
        return url

