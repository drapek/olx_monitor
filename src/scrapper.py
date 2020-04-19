import datetime
import json
import random
import time
import pickle
import requests
from bs4 import BeautifulSoup

import settings
from email_sender import EmailClient
from fake_request_header import olx_request_headers
from logger import log_print
from messenger_client import MessengerClient


class Scrapper:
    INTERRUPT_PROCESS = False
    FOUND_OFFERS_IDS = set()
    RECIPIENT_EMAILS = []
    messenger_client = None
    email_client = None

    def __init__(self, recipient_emails=()):
        # primitive way of storing data in file
        try:
            with open(settings.DB_FILE, 'rb') as file:
                self.FOUND_OFFERS_IDS = pickle.load(file)
        except FileNotFoundError:
            pass

        self.RECIPIENT_EMAILS = recipient_emails
        self.messenger_client = MessengerClient(settings.MESSENGER_APP_TOKEN, settings.MESSENGER_RECIPIENTS)
        self.email_client = EmailClient()

    def run_in_loop(self, sites, interval=settings.SCAN_INTERVAL_SEC, working_hours=settings.WORKING_HOURS):
        while not self.INTERRUPT_PROCESS:
            if not self.is_now_working_hour(working_hours):
                log_print(f'We have currently non working hours. Current working hours are {working_hours[0]} - '
                          f'{working_hours[1]}')
                log_print(f'sleeping for {interval/60} min')
                time.sleep(interval)
                continue

            for site in sites:
                random_time = random.randint(5, 15) * 60
                log_print(f'sleeping for {random_time / 60} min to prevent recognizing as BOT')
                time.sleep(random_time)  # Wait random time to be not banned for being a BOT
                self.scan_site(site['url'], site['cookie'])
                log_print(f"Requested url: {site['url']}", message_type=3)

            log_print(f'sleeping for {interval / 60} min')
            time.sleep(interval)

    def is_now_working_hour(self, working_hours):
        return working_hours[0] <= datetime.datetime.now().hour < working_hours[1]

    def scan_site(self, url, cookie=''):
        try:
            page = requests.get(url, headers=self._generate_request_headers(cookie))

            if page.status_code != 200:
                raise ConnectionError(f"Can't fetch data. {page.status_code} : {page.content}")

            self.analyze_html_page(page.content)
        except Exception as e:
            log_print(f"Coudn't fetch the url {url}. The error: {e}", message_type=1)

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
                self._send_messenger_msg(offer_data)
                self.FOUND_OFFERS_IDS.add(offer_id)
                self._dump_FOUND_OFFERS_IDS_into_DB()
                log_print(f"Found: {offer_data}")

    def _analyze_offer(self, offer):
        offer_data = {
            'title': self._get_value_or_none("offer.find('strong').text", offer),
            'price': self._get_value_or_none("offer.find('p', {'class': 'price'}).find('strong').text", offer),
            'localization': self._get_value_or_none("offer.find('td', "
                                                    "{'class': 'bottom-cell'}).find_all('span')[0].text", offer),
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
        email_body = f'<!DOCTYPE html>' \
                     f'<html lang="pl"><body>' \
                     f'<b>Cześć, znanazłem nowe ogłoszenie! </b><h1>{offer_data["title"]}</h1> ' \
                     f'<table><tr><td><img src="{offer_data["image_url"]}" /></td></tr>' \
                     f'<tr><td><b>Cena: {offer_data["price"]}</b></td></tr>' \
                     f'<tr><td><p>Data dodania: {offer_data["add_time"]}</p></td></tr>' \
                     f'<tr><td><p>Lokalizajca: {offer_data["localization"]}</p></td></tr></table>' \
                     f'<a href="{offer_data["offer_url"]}">Link do aukcji</a>' \
                     f'</body></html>'

        self.email_client.send_email(self.RECIPIENT_EMAILS, "Drapek wyszukiwacz - nowe ogłoszenie na OLX", email_body)

    def _send_messenger_msg(self, offer_data):
        message = f'Cześć znalazłem nowe ogłoszenie! \n\n' \
                  f'{offer_data["title"]} za {offer_data["price"]}. \n\n' \
                  f'Lokalizacja: {offer_data["localization"]} \n' \
                  f'Dodano {offer_data["add_time"]}. \n' \
                  f'Link {offer_data["offer_url"]}'
        self.messenger_client.send_message(message)
        self.messenger_client.send_image(offer_data["image_url"])

    def _dump_FOUND_OFFERS_IDS_into_DB(self):
        with open(settings.DB_FILE, 'wb+') as file:
            pickle.dump(self.FOUND_OFFERS_IDS, file)

    def _generate_request_headers(self, req_cookie):
        headers = olx_request_headers
        current_timestamp = int(time.time())
        cookie = req_cookie + f' lister_lifecycle={current_timestamp};'
        headers['cookie'] = cookie
        return headers


def send_debug_messenger_msg():
    offer = {"title": "Nowoczesne i komfortowe mieszkanie 2 pokoje Warszawa \u2013 Ochota", "price": "1 650 z\u0142",
             "localization": "Warszawa, Ochota",
             "add_time": "dzisiaj 15:05",
             "image_url": "https://apollo-ireland.akamaized.net:443/v1/files/uhm01bee0c54-PL/image;s=261x203",
             "offer_url": "https://www.olx.pl/oferta/nowoczesne-i-komfortowe-mieszkanie-2-pokoje-warszawa-ochota-CID3-"
                          "IDEl1KI.html#b8e2255afb",
             "data_id": "596065068"}
    scrapper = Scrapper()
    scrapper._send_messenger_msg(offer)


if __name__ == '__main__':
    send_debug_messenger_msg()
