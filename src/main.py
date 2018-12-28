import settings
from scrapper import Scrapper


def main():
    s = Scrapper(recipient_emails=settings.RECIPIENT_EMAILS)
    s.run_in_loop(settings.OLX_SITES_TO_MONITOR)


if __name__ == '__main__':
    main()
