import er.downloader
import settings
import storage


def main():
    subject_storage = storage.get_storage(settings)
    downloader = er.downloader.SubjectDownloader(settings.ER_TOKEN, settings.ER_HOST, subject_storage, settings.SERVER_URL)
    downloader.download_subjects_and_tracks()


if __name__ == "__main__":
    main()