import json
import datetime
import random

import dasclient.dasclient

DEFAULT_DAYS = 16

class SubjectDownloader:
    def __init__(self, token, host, storage, api_host=None, since=None):
        self.token = token
        self.host = host
        self.api_host = api_host
        service_root = self.host + '/api/v1.0'
        self.client = dasclient.dasclient.DasClient(token=token, service_root=service_root)
        self.storage = storage
        self.since = since
        if not since:
            self.since = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=16)

    def fixup_host(self, obj):
        if self.api_host:
            data = json.dumps(obj)
            data = data.replace(self.host, self.api_host)
            obj = json.loads(data)
        return obj

    def download_subjects_and_tracks(self):
        subjects = self.client.get_subjects()
        new_subjects = {"data": []}

        # save if tracks are available?
        keep_keys = ['id', 'name', 'sex', 'subject_type', 'subject_subtype', 'image_url', 'last_position', 'common_name']

        for subject in subjects:
            if (subject["tracks_available"] == true):
                subject = {k:v for k,v in subject.items() if k in keep_keys}
                new_subjects["data"].append(subject)
                if subject.get("last_position") and subject["last_position"].get("properties"):
                    subject["last_position"]["properties"]["image"] = subject["last_position"]["properties"]["image"].replace(".svg", ".png")
                subject["image_url"] = subject["image_url"].replace(".svg", ".png")
                # subject["color"] = '#{:02x}{:02x}{:02x}'.format(*map(lambda x: random.randint(0, 255), range(3)))
                self.download_track(subject)
                self.storage.save_subject_image(subject)

        self.storage.save_subjects(self.fixup_host(new_subjects))

    def download_track(self, subject):
        track = self.client.get_subject_tracks(subject['id'], start=self.since)
        self.storage.save_subject_track(subject, self.fixup_host(track))


