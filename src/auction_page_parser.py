import dataclasses
import datetime
import json
import re
import traceback
from abc import ABC, abstractmethod
from datetime import datetime

from bs4 import BeautifulSoup

import settings
from data_classes.house import HouseOffer
from logger import log_print
from page_downloander import PageDownloader
from utils import Bs4SafeCodeEvaluator


class AuctionPageParser:
    def __init__(self, found_offers_set, message_sender, cookie=''):
        self.page_downloader = PageDownloader(cookie)
        self.found_offers_set = found_offers_set
        self.message_sender = message_sender

    def scan_site(self, url):
        try:
            page = self.page_downloader.get_page(url)

            parser = None
            if 'otodom.pl' in url:
                parser = OtoDomParser
            # TODO add Car data class and update the Parsers
            # if 'olx.pl' in url:
            #     parser = OlxParser
            # if 'sprzedajemy.pl' in url:
            #     parser = SprzedajemyParser
            # if 'otomoto.pl' in url:
            #     parser = OtomotoParser
            # if parser is None:
            #     log_print(f"[ERROR] couldn't find Page Parser for the site {url}")
            #     return

            return parser(downloader=self.page_downloader, found_offers_set=self.found_offers_set,
                          message_sender=self.message_sender, page_url=url).analyze_html_page(page.content)
        except Exception as e:
            log_print(f"Coudn't fetch the url {url}. The error: {e}", message_type=1)
            print(traceback.format_exc())


class PageParser(ABC):
    def __init__(self, downloader, found_offers_set, message_sender, page_url):
        self.page_downloader = downloader
        self.found_offers_set = found_offers_set
        self.message_sender = message_sender
        self.page_url = page_url

    def analyze_html_page(self, raw_html_content):
        """
        The main method - Recommended to not override this method
        :param raw_html_content: the raw html content
        :return: dict - {'offer_id': { offer_data }, ...}
        """
        soup = BeautifulSoup(raw_html_content, 'html.parser')

        found_offers_html = self.get_offers_list_html(soup)

        offers = []
        for offer_html in found_offers_html:
            if not self.is_offer_element_valid(offer_html):
                continue
            offer = self.analyze_offer(offer_html)
            if offer.id not in self.found_offers_set:
                self.perform_action_on_new_offer(offer)

        return offers

    def perform_action_on_new_offer(self, offer):
        self.message_sender.send_messages(offer)
        self._save_found_offer_into_file(offer)
        self.found_offers_set.add(offer.id)
        log_print(f"Found: {offer}")

    @staticmethod
    def _save_found_offer_into_file(offer: HouseOffer) -> None:
        with open(settings.OUT_FILE, 'a+') as out_file:
            out_file.writelines(json.dumps(dataclasses.asdict(offer)) + ",\n")

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
        :return: DataClass - the data class with all needed offer parameters
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


# class OlxParser(PageParser):
#     def get_offers_list_html(self, page_html):
#         return page_html.find_all('table', {'summary': "Ogłoszenia"})[0].find_all("table", {'summary': "Ogłoszenie"})
#
#     def analyze_offer(self):
#         offer_data = {
#             'title': safe_eval.get_value_or_none("self.offer_html.find('strong').text"),
#             'price': safe_eval.get_value_or_none("self.offer_html.find('p', {'class': 'price'}).find('strong').text"),
#             'localization':
#                 safe_eval.get_value_or_none("self.offer_html.find('td', {'class': 'bottom-cell'}).find_all('span')[0].text",
#                                   offer_html),
#             'add_time':
#                 safe_eval.get_value_or_none("self.offer_html.find('td', {'class': 'bottom-cell'}).find_all('span')[1].text",
#                                   offer_html),
#             'image_url': safe_eval.get_value_or_none("self.offer_html.find('img').attrs['src']"),
#             'offer_url': safe_eval.get_value_or_none("self.offer_html.find('a').attrs['href']"),
#             'data_id': offer_html.get('data-id')
#         }
#         return offer_data
#
#
# class SprzedajemyParser(PageParser):
#     def get_offers_list_html(self, page_html):
#         return page_html.find_all('ul', class_='normal')[0].find_all('li')
#
#     def is_offer_element_valid(self):
#         return 'offer-' in offer_html.attrs.get('id', '')
#
#     def analyze_offer(self):
#         offer_url = safe_eval.get_value_or_none("self.offer_html.find('a').attrs['href']")
#         if 'https://' not in offer_url:
#             offer_html = 'https://sprzedajemy.pl' + offer_html
#         offer_data = {
#             'title': safe_eval.get_value_or_none("self.offer_html.find('h2', class_='title').text"),
#             'price': safe_eval.get_value_or_none("self.offer_html.find('span', class_='price').text"),
#             'localization': safe_eval.get_value_or_none("self.offer_html.find('strong', class_='city').text"),
#             'add_time': safe_eval.get_value_or_none("self.offer_html.find('time', class_='time').attrs['datetime']"),
#             'image_url': safe_eval.get_value_or_none("self.offer_html.find('img').attrs['src']"),
#             'offer_url': offer_url,
#             'data_id': offer_html.attrs['id'][len('offer-'):]  # strip the 'offer-' prefix
#         }
#         return offer_data
#
#
# class OtomotoParser(PageParser):
#     def get_offers_list_html(self, page_html):
#         return page_html.find_all('div', class_='offers')[0].find_all('article')
#
#     def analyze_offer(self):
#         offer_data = {
#             'title': safe_eval.get_value_or_none("self.offer_html.find('a', class_='offer-title__link').attrs['title']"),
#             'price': safe_eval.get_value_or_none("self.offer_html.find('span', class_='offer-price__number').text"),
#             'localization': safe_eval.get_value_or_none("self.offer_html.find('h4', class_='ds-location').text"),
#             'add_time': f'empty - but the offer was found at {datetime.now()}',
#             'image_url': safe_eval.get_value_or_none("self.offer_html.find('img').attrs['data-src']"),
#             'offer_url': safe_eval.get_value_or_none("self.offer_html.find('a').attrs['href']"),
#             'data_id': offer_html.attrs['data-ad-id']  # strip the 'offer-' prefix
#         }
#         return offer_data


class OtoDomParser(PageParser):
    def get_offers_list_html(self, page_html):
        return page_html.find_all('h2', {'data-cy': 'search.listing.title'})[0].parent.find_all('li')

    def analyze_offer(self, offer_html):
        safe_eval = Bs4SafeCodeEvaluator(offer_html, self.page_url)
        internal_id = None
        portal_offer_id = None
        dict_data = {
            'tittle': safe_eval.get_value_or_none("self.offer_html.find('h3', {'data-cy': 'listing-item-title'}).text"),
            'price': safe_eval.get_value_or_none("self.offer_html.find_all('p')[1].text"),
            'add_date': f'offer was found at {datetime.now()}',
            'image_url': safe_eval.get_value_or_none("self.offer_html.find('img').attrs['src']")}

        offer_url = safe_eval.get_value_or_none("self.offer_html.find('a').attrs['href']")
        if offer_url:
            offer_url = f'https://otodom.pl{offer_url}'
            regex_res = re.match(r'.*ID(?P<id>.*)$', offer_url)
            portal_offer_id = str(datetime.now().timestamp()) if regex_res is None else regex_res.group('id')
            internal_id = f"{self.__class__.__name__}_{portal_offer_id}"
            dict_data.update(self.analyze_offer_details_page(offer_url))

        localization = safe_eval.get_value_or_none("self.offer_html.find_all('p')[0].text")
        prefix_to_cut = 'Mieszkanie na sprzedaż:'
        if localization and prefix_to_cut in localization:
            localization = localization[len(prefix_to_cut):]

        offer = HouseOffer(id=internal_id, offer_url=offer_url, portal_offer_id=portal_offer_id,
                           localization=localization, **dict_data)
        return offer

    def analyze_offer_details_page(self, url):
        """
        :param url: the url for details page
        :return: dict with params that will be used ass attribs into dataclass HouseOffer
        """
        try:
            page = self.page_downloader.get_page(url)
            offer_html = BeautifulSoup(page.content, 'html.parser')
            safe_eval = Bs4SafeCodeEvaluator(offer_html, url)
            return {
                'rooms_number': safe_eval.get_value_or_none(
                    "int(self.offer_html.find_all(text='Liczba pokoi')[0].parent.parent.contents[1].text)"),
                'floor': safe_eval.get_value_or_none(
                    "self.offer_html.find_all(text='Piętro')[0].parent.parent.contents[1].text"),
                'flat_area': safe_eval.get_value_or_none(
                    "self.offer_html.find_all(text='Powierzchnia')[0].parent.parent.contents[3].text"),
            }
        except Exception as e:
            log_print(f'Impossible to download page {url}. Details: {e}',)
            return {}
