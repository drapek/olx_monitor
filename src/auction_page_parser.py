import time
from abc import ABC, abstractmethod
from datetime import datetime

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
            if 'otomoto.pl' in url:
                parser = OtomotoParser()
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
    def analyze_html_page(self, raw_html_content):
        """
        The main method - Recommended to not override this method
        :param raw_html_content: the raw html content
        :return: dict - {'offer_id': { offer_data }, ...}
        """
        soup = BeautifulSoup(raw_html_content, 'html.parser')

        found_offers_html = self.get_offers_list_html(soup)

        offers_dict = {}
        for offer_html in found_offers_html:
            if not self.is_offer_element_valid(offer_html):
                continue
            offer_data = self.analyze_offer(offer_html)
            offer_id = f"{self.__class__.__name__}_{offer_data['data_id']}"
            offers_dict[offer_id] = offer_data

        return offers_dict

    @abstractmethod
    def get_offers_list_html(self, page_html):
        """
        This method should find the all elements on the page (like div, h2, etc) that consist the offers.
        :param page_html: whole page html parsed by beautiful soup
        :return: list of parsed html elements that should be an offers. One element in list is equal to one offer
        """
        ...

    @abstractmethod
    def analyze_offer(self, offer_html):
        """
        Make an analysis of the provided html offer to create offer_dict that consist the all needed data
        :param offer_html: the one offer html - this should be an beautiful soup parsed html
        :return: dict - the data dict with all needed offer parameters
        """
        ...

    def is_offer_element_valid(self, offer_html):
        """
        Overriding of this method is not required. This methods check if given html is an valid offer, by default
        all offers are valid.
        :param offer_html: the soup objects that consists the offer html
        :return:
        """
        return True


class OlxParser(PageParser):
    def get_offers_list_html(self, page_html):
        return page_html.find_all('table', {'summary': "Ogłoszenia"})[0].find_all("table", {'summary': "Ogłoszenie"})

    def analyze_offer(self, offer_html):
        offer_data = {
            'title': get_value_or_none("offer_html.find('strong').text", offer_html),
            'price': get_value_or_none("offer_html.find('p', {'class': 'price'}).find('strong').text", offer_html),
            'localization':
                get_value_or_none("offer_html.find('td', {'class': 'bottom-cell'}).find_all('span')[0].text",
                                  offer_html),
            'add_time':
                get_value_or_none("offer_html.find('td', {'class': 'bottom-cell'}).find_all('span')[1].text",
                                  offer_html),
            'image_url': get_value_or_none("offer_html.find('img').attrs['src']", offer_html),
            'offer_url': get_value_or_none("offer_html.find('a').attrs['href']", offer_html),
            'data_id': offer_html.get('data-id')
        }
        return offer_data


class SprzedajemyParser(PageParser):
    def get_offers_list_html(self, page_html):
        return page_html.find_all('ul', class_='normal')[0].find_all('li')

    def is_offer_element_valid(self, offer_html):
        return 'offer-' in offer_html.attrs.get('id', '')

    def analyze_offer(self, offer_html):
        offer_data = {
            'title': get_value_or_none("offer_html.find('h2', class_='title').text", offer_html),
            'price': get_value_or_none("offer_html.find('span', class_='price').text", offer_html),
            'localization': get_value_or_none("offer_html.find('strong', class_='city').text", offer_html),
            'add_time': get_value_or_none("offer_html.find('time', class_='time').attrs['datetime']", offer_html),
            'image_url': get_value_or_none("offer_html.find('img').attrs['src']", offer_html),
            'offer_url': 'https://sprzedajemy.pl' + get_value_or_none("offer_html.find('a').attrs['href']", offer_html),
            'data_id': offer_html.attrs['id'][len('offer-'):]  # strip the 'offer-' prefix
        }
        return offer_data


class OtomotoParser(PageParser):
    def get_offers_list_html(self, page_html):
        return page_html.find_all('div', class_='offers')[0].find_all('article')

    def analyze_offer(self, offer_html):
        offer_data = {
            'title': get_value_or_none("offer_html.find('a', class_='offer-title__link').attrs['title']", offer_html),
            'price': get_value_or_none("offer_html.find('span', class_='offer-price__number').text", offer_html),
            'localization': get_value_or_none("offer_html.find('h4', class_='ds-location').text", offer_html),
            'add_time': f'empty - but the offer was found at {datetime.now()}',
            'image_url': get_value_or_none("offer_html.find('img').attrs['data-src']", offer_html),
            'offer_url': get_value_or_none("offer_html.find('a').attrs['href']", offer_html),
            'data_id': offer_html.attrs['data-ad-id']  # strip the 'offer-' prefix
        }
        return offer_data
