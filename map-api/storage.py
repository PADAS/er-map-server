import logging
import json
import tempfile
import mimetypes

import boto3


logger = logging.getLogger(__name__)


class EAPStorage:
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

    def get_user_credentials(self, username):
        path = f'{self.users_dir}/{username}'
        with tempfile.TemporaryFile('w+b') as fh:
            self.download_file(path, fh)
            fh.seek(0)
            return json.loads(fh.read().decode())

