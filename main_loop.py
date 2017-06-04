from scraper import do_scrape
import settings
import time
import sys
import traceback


def verify_tokens():
    if not settings.SLACK_TOKEN:
        print('SLACK_TOKEN must be set')
        sys.exit(1)
    if not settings.GOOGLE_MAPS_TOKEN:
        print('GOOGLE_MAPS_TOKEN must be set')
        sys.exit(1)


def main():
    while True:
        print("{}: Starting scrape cycle".format(time.ctime()))
        try:
            do_scrape()
        except Exception as exc:
            print("Error with the scraping:", sys.exc_info()[0])
            traceback.print_exc()
        else:
            print("{}: Successfully finished scraping".format(time.ctime()))
        time.sleep(settings.SLEEP_INTERVAL)


if __name__ == "__main__":
    try:
        verify_tokens()
        main()
    except KeyboardInterrupt:
        print("Exiting....")
