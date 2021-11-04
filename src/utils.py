import re  # This is used by code that is evaluated
from logger import log_print


def get_value_or_none(risky_code, offer_html):
    """
    Some elements on the site can be not present. So to prevent exiting just pass that kind of exceptions.
    :param risky_code:
    :param offer_html: this param is need to provide context for the evaluated risky_code.
    :return:
    """
    try:
        result = eval(risky_code)
        result = " ".join(result.split())  # remove redundant white characters like spaces \t \n etc.
        return result
    except Exception as e:
        log_print(f"[Warring] Coudn't parse the element {risky_code}. Exception occured: {e}")
        return None
