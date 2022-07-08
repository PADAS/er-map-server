import datetime
import logging

import er.downloader
import settings
import storage


logger = logging.getLogger(__name__)

def main():
    for name, public_site in settings.PUBLIC_SITES.items():
        subject_storage = storage.get_storage(settings, public_site)
        for er_site in public_site.er_sites:
            since = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=er_site.show_track_days)
            downloader = er.downloader.SubjectDownloader(er_site.token, er_site.host,
             subject_storage, settings.SERVER_URL, public_site.name, since)
            try:
                downloader.download_subjects_and_tracks()
            except Exception as ex:
                logger.exception(f"Error with site {er_site.host}")
                


if __name__ == "__main__":
    main()