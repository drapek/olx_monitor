import datetime
import pickle
import random
import time

import settings
from auction_page_parser import AuctionPageParser
from logger import log_print
from message_sender import MessageSender


class Scrapper:
    INTERRUPT_PROCESS = False
    FOUND_OFFERS_IDS = set()
    message_sender = None

    def __init__(self, recipient_emails=()):
        self._read_offers_ids_from_db()
        self.message_sender = MessageSender(recipient_emails)

    def _read_offers_ids_from_db(self):
        # primitive way of storing data in file
        try:
            with open(settings.DB_FILE, 'rb') as file:
                self.FOUND_OFFERS_IDS = pickle.load(file)
                log_print(f'read offers id from the database {self.FOUND_OFFERS_IDS}', message_type=3)
        except FileNotFoundError:
            pass

    def run_in_loop(self, sites, interval=settings.SCAN_INTERVAL_SEC, working_hours=settings.WORKING_HOURS):
        while not self.INTERRUPT_PROCESS:
            # if not self.is_now_working_hour(working_hours):
            #     log_print(f'We have currently non working hours. Current working hours are {working_hours[0]} - '
            #               f'{working_hours[1]}')
            #     log_print(f'sleeping for {interval/60} min')
            #     time.sleep(interval)
            #     continue

            for site in sites:
                random_time = random.randint(2, 5) * 60
                log_print(f'sleeping for {random_time / 60} min to prevent recognizing as BOT')
                # time.sleep(random_time)  # Wait random time to be not banned for being a BOT
                AuctionPageParser(self.FOUND_OFFERS_IDS, self.message_sender, site['cookie']).scan_site(site['url'])
                self._save_offers_ids_to_database()
                log_print(f"Requested url: {site['url']}", message_type=3)

            log_print(f'sleeping for {interval / 60} min')
            time.sleep(interval)

    @staticmethod
    def is_now_working_hour(working_hours):
        return working_hours[0] <= datetime.datetime.now().hour < working_hours[1]

    def _save_offers_ids_to_database(self):
        with open(settings.DB_FILE, 'wb+') as file:
            pickle.dump(self.FOUND_OFFERS_IDS, file)
