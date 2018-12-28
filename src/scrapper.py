import json
import random
import time
import pickle
import requests
from bs4 import BeautifulSoup

import settings
from email_sender import EmailSender
from logger import log_print


class Scrapper:
    INTERRUPT_PROCESS = False
    FOUND_OFFERS_IDS = set()
    RECIPIENT_EMAILS = []

    def __init__(self, recipient_emails=()):
        # primitive way of storing data in file
        try:
            with open(settings.DB_FILE, 'rb') as file:
                self.FOUND_OFFERS_IDS = pickle.load(file)
        except FileNotFoundError:
            pass

        self.RECIPIENT_EMAILS = recipient_emails

    def run_in_loop(self, urls=list(), interval=settings.SCAN_INTERVAL_SEC, ):
        while not self.INTERRUPT_PROCESS:
            for url in urls:
                self.scan_site(url)
                log_print(f"Requested url: {url}", message_type=3)
                time.sleep(random.randint(5, 20))  # Wait random time to be not banned for botting
            time.sleep(interval)

    def scan_site(self, url):
        page = requests.get(url)

        if page.status_code != 200:
            raise ConnectionError(f"Can't fetch data. {page.status_code} : {page.content}")

        self.analyze_html_page(page.content)

    def analyze_html_page(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')

        found_offers = soup.find_all('table', {'summary': "Ogłoszenia"})[0]. \
            find_all("table", {'summary': "Ogłoszenie"})

        for offer in found_offers:
            offer_data = self._analyze_offer(offer)
            offer_id = offer_data.get('data_id')
            if offer_id not in self.FOUND_OFFERS_IDS:
                self._save_found_offer_into_file(offer_data)
                self._send_email(offer_data)
                self._dump_FOUND_OFFERS_IDS_into_DB()
                log_print(f"Found: {offer_data}")
            self.FOUND_OFFERS_IDS.add(offer_id)

    def _analyze_offer(self, offer):

        offer_data = {
            'title': self._get_value_or_none("offer.find('strong').text", offer),
            'price': self._get_value_or_none("offer.find('p', {'class': 'price'}).find('strong').text", offer),
            'localization': self._get_value_or_none("offer.find('td', {'class': 'bottom-cell'}).find_all('span')[0].text",
                                                    offer),
            'add_time': self._get_value_or_none("offer.find('td', {'class': 'bottom-cell'}).find_all('span')[1].text",
                                                offer),
            'image_url': self._get_value_or_none("offer.find('img').attrs['src']", offer),
            'offer_url': self._get_value_or_none("offer.find('a').attrs['href']", offer),
            'data_id': offer.get('data-id')
        }
        return offer_data

    def _get_value_or_none(self, risky_code, offer):
        """
        Some elements on the site can be not present. So to prevent exiting just pass that kind of exceptions.
        :param risky_code:
        :param offer: this param is need to provide context for the evaluated risky_code.
        :return:
        """
        try:
            result = eval(risky_code)
            return result.strip()
        except Exception as e:
            return None

    def _save_found_offer_into_file(self, offer):
        with open(settings.OUT_FILE, 'a+') as out_file:
            out_file.writelines(json.dumps(offer)+",\n")

    def _send_email(self, offer_data):
        es = EmailSender()
        email_body = f'<!DOCTYPE html>' \
                     f'<html lang="pl"><body>' \
                     f'<b>Cześć, znanazłem nowe ogłoszenie! </b><h1>{offer_data["title"]}</h1> ' \
                     f'<table><tr><td><img src="{offer_data["image_url"]}" /></td></tr>' \
                     f'<tr><td><b>Cena: {offer_data["price"]}</b></td></tr>' \
                     f'<tr><td><p>Data dodania: {offer_data["add_time"]}</p></td></tr>' \
                     f'<tr><td><p>Lokalizajca: {offer_data["localization"]}</p></td></tr></table>' \
                     f'<a href="{offer_data["offer_url"]}">Link do aukcji</a>' \
                     f'</body></html>'

        es.send_email(self.RECIPIENT_EMAILS, "Drapek wyszukiwacz - nowe ogłoszenie na OLX", email_body)

    def _dump_FOUND_OFFERS_IDS_into_DB(self):
        with open(settings.DB_FILE, 'wb+') as file:
            pickle.dump(self.FOUND_OFFERS_IDS, file)
