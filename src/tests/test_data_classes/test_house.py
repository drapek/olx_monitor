from datetime import datetime

from data_classes.house import HouseOffer


def test_house_dataclass_happy_path():
    house = HouseOffer(id='olx_234', tittle='Title 123', price=600000, flat_area=53.3, rooms_number=3,
                       image_url='https://img.pl/img/1', offer_url='https://olx.pl/offer/1234',
                       add_date=datetime(2021, 11, 11, 15, 45), localization='Wola, Góreczewska 128')
    expected_message_body = ('Cześć znalazłem nowe ogłoszenie! '
                             '\n\n Title 123 \n\n'
                             'Metraż: 53.3 \n'
                             'Liczba pokoi: 3 \n'
                             'Cena: 600000 \n'
                             'Lokalizacja: Wola, Góreczewska 128 \n'
                             'Dodano: 2021-11-11 15:45:00 \n'
                             'Link: https://olx.pl/offer/1234')
    assert house.message_body_messenger() == expected_message_body


