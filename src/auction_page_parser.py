import abc
import time
from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup

from fake_request_header import olx_request_headers
from logger import log_print
from utils import get_value_or_none


class AuctionPageParser:

    @staticmethod
    def scan_site(url, cookie=''):
        try:
            page = requests.get(url, headers=AuctionPageParser._generate_request_headers(cookie))

            if page.status_code != 200:
                raise ConnectionError(f"Can't fetch data. {page.status_code} : {page.content}")

            parser = None
            if 'olx.pl' in url:
                parser = OlxParser()
            if 'sprzedajemy.pl' in url:
                parser = SprzedajemyParser()
            if parser is None:
                log_print(f"[ERROR] couldn't find Page Parser for the site {url}")
                return

            return parser.analyze_html_page(page.content)
        except Exception as e:
            log_print(f"Coudn't fetch the url {url}. The error: {e}", message_type=1)


    @staticmethod
    def _generate_request_headers(req_cookie):
        headers = olx_request_headers
        current_timestamp = int(time.time())
        cookie = req_cookie + f' lister_lifecycle={current_timestamp};'
        headers['cookie'] = cookie
        return headers


class PageParser(ABC):
    @abstractmethod
    def analyze_html_page(self, html_content):
        ...


class OlxParser(PageParser):
    def analyze_html_page(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')

        found_offers_html = soup.find_all('table', {'summary': "Ogłoszenia"})[0]. \
            find_all("table", {'summary': "Ogłoszenie"})

        offers_dict = {}
        for offer_html in found_offers_html:
            offer_data = self.analyze_offer(offer_html)
            offer_id = offer_data.get('data_id')
            offers_dict[offer_id] = offer_data

        return offers_dict

    def analyze_offer(self, offer_html):
        offer_data = {
            'title': get_value_or_none("offer.find('strong').text"),
            'price': get_value_or_none("offer.find('p', {'class': 'price'}).find('strong').text"),
            'localization': get_value_or_none("offer.find('td', {'class': 'bottom-cell'}).find_all('span')[0].text"),
            'add_time': get_value_or_none("offer.find('td', {'class': 'bottom-cell'}).find_all('span')[1].text"),
            'image_url': get_value_or_none("offer.find('img').attrs['src']"),
            'offer_url': get_value_or_none("offer.find('a').attrs['href']"),
            'data_id': offer_html.get('data-id')
        }
        return offer_data


class SprzedajemyParser:
    ...
