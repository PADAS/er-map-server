import json
import datetime
import random

from erclient import ERClient

DEFAULT_DAYS = 16

class SubjectDownloader:
    def __init__(self, token, host, storage, api_host=None, public_name=None, since=None, until=None):
        self.token = token
        self.host = host
        self.api_host = api_host
        self.public_name = public_name
        service_root = self.host + '/api/v1.0'
        self.client = ERClient(token=token, service_root=service_root)
        self.storage = storage
        self.since = since
        if not since:
            self.since = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=16)
        self.until = until

    def fixup_host(self, obj):
        if self.api_host:
            data = json.dumps(obj)
            data = data.replace(self.host, self.api_host + f"/{self.public_name}")
            obj = json.loads(data)
        return obj

    def fixeup_latest_track_points(self, subjects, latest_track_points):
        for subject in subjects:
            subject_id = subject["id"]
            if subject_id in latest_track_points:
                lon, lat, recorded_at = latest_track_points[subject_id]
                subject["last_position"]["geometry"]["coordinates"] = [lon, lat]
                subject["last_position"]["properties"]["coordinateProperties"]["time"] = recorded_at
                subject["last_position"]["properties"]["DateTime"] = recorded_at
                subject["last_position_date"] = recorded_at


    def download_subjects_and_tracks(self):
        subjects = self.client.get_subjects()

        new_subjects = []
        latest_subject_track_points = {}

        # save if tracks are available?
        keep_keys = ['id', 'name', 'sex', 'subject_type', 'subject_subtype', 'image_url', 'last_position', 'common_name']

        for subject in subjects:
            if (subject["tracks_available"] == True):
                subject = {k:v for k,v in subject.items() if k in keep_keys}
                new_subjects.append(subject)
                #if subject.get("last_position") and subject["last_position"].get("properties"):
                #    subject["last_position"]["properties"]["image"] = subject["last_position"]["properties"]["image"].replace(".svg", ".png")
                #subject["image_url"] = subject["image_url"].replace(".svg", ".png")
                # subject["color"] = '#{:02x}{:02x}{:02x}'.format(*map(lambda x: random.randint(0, 255), range(3)))
                newest_track_point = self.download_track(subject)
                if newest_track_point:
                    latest_subject_track_points[subject["id"]] = newest_track_point
                self.storage.save_subject_image(subject)
        self.fixeup_latest_track_points(subjects, latest_subject_track_points)
        self.storage.save_subjects(self.fixup_host({"data": new_subjects}))

    def download_track(self, subject):
        track = self.client.get_subject_tracks(subject['id'], start=self.since, end=self.until)
        self.storage.save_subject_track(subject, self.fixup_host(track))
        newest_track_point = None
        if track and track.get("features"):
            try:
                newest_track_point = (
                    track["features"][0]["geometry"]["coordinates"][0][0],
                    track["features"][0]["geometry"]["coordinates"][0][1],
                    track["features"][0]["properties"]["coordinateProperties"]["times"][0]
                )
            except TypeError:
                pass
        return newest_track_point


