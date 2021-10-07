import er.downloader
import settings
import storage


def main():
    for name, public_site in settings.PUBLIC_SITES.items():
        subject_storage = storage.get_storage(settings, public_site)
        for er_site in public_site.er_sites:
            downloader = er.downloader.SubjectDownloader(er_site.token, er_site.host, subject_storage, settings.SERVER_URL, public_site.name)
            downloader.download_subjects_and_tracks()


if __name__ == "__main__":
    main()