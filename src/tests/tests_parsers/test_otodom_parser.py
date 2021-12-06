from bs4 import BeautifulSoup

from auction_page_parser import OtoDomParser


def test_extracting_id():
    example_offer = '''<li class="css-x9km8e es62z2j30">
    <a data-cy="listing-item-link" data-cy-viewed="false" href="/pl/oferta/metro-mlynow-kamienica-po-remoncie-ID4ekdQ" 
    class="css-137nx56 es62z2j27">
    </li>
    '''
    parser = OtoDomParser()
    offer_soup = BeautifulSoup(example_offer, 'html.parser')
    resp = parser.analyze_offer(offer_soup)
    assert resp.portal_offer_id == '4ekdQ'
