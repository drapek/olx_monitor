import requests
import time

from retry import retry

from fake_request_header import olx_request_headers


class PageDownloader:
    def __init__(self, cookie=''):
        self._request_headers = PageDownloader._generate_request_headers(cookie)

    @staticmethod
    def _generate_request_headers(req_cookie):
        headers = olx_request_headers
        current_timestamp = int(time.time())
        cookie = req_cookie + f' lister_lifecycle={current_timestamp};'
        headers['cookie'] = cookie
        return headers

    @retry(tries=3, delay=60)
    def get_page(self, url):
        page = requests.get(url, headers=self._request_headers)

        if page.status_code != 200:
            raise ConnectionError(f"Can't fetch data. {page.status_code} : {page.content}")
        return page
