
from logger import log_print


class Bs4SafeCodeEvaluator:
    def __init__(self, offer_html_soup, offer_url):
        self.offer_html = offer_html_soup
        self.offer_url = offer_url

    def get_value_or_none(self, risky_code):
        """
        Some elements on the site can be not present. So to prevent exiting just pass that kind of exceptions.
        :param risky_code:
        :return: Value or None - never raise the Exception!
        """
        try:
            result = eval(risky_code)
            if type(result) == str:
                result = result.strip()
            return result
        except Exception as e:
            log_print(f"[Warring] Coudn't parse the element {risky_code}. "
                      f"Exception occured on site {self.offer_url}."
                      f"Body of the evaluated html is: {self.offer_html}"
                      f"The exception was: {e}")
            return None
