from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class HouseOffer:
    """
    Class for storing house data and creating message for the User
    """
    id: str
    portal_offer_id: str = ''
    tittle: str = ''
    price: float = 0.0
    flat_area: float = 0.0
    rooms_number: int = 0
    floor: str = ''
    image_url: str = ''
    offer_url: str = ''
    add_date: datetime = None
    localization: str = ''

    def message_body_messenger(self) -> str:
        return ('Cześć znalazłem nowe ogłoszenie! \n\n '
                f'{self.tittle} \n\n'
                f'Metraż: {self.flat_area} \n'
                f'Liczba pokoi: {self.rooms_number} \n'
                f'Cena: {self.price} \n'
                f'Lokalizacja: {self.localization} \n'
                f'Dodano: {self.add_date} \n'
                f'Link: {self.offer_url}')

    def message_body_html(self):
        return (f'<b>Cześć, znanazłem nowe ogłoszenie! </b><h1>{self.tittle}</h1> '
                f'<table><tr><td><img src="{self.image_url}" /></td></tr>'
                f'<tr><td><b>Cena: {self.price}</b></td></tr>'
                f'<tr><td><p>Data dodania: {self.add_date}</p></td></tr>'
                f'<tr><td><p>Lokalizajca: {self.localization}</p></td></tr></table>'
                f'<a href="{self.offer_url}">Link do aukcji</a>')
