from dataclasses import dataclass

from data_classes.base import BaseOffer


@dataclass(frozen=True)
class HouseOffer(BaseOffer):
    """
    Class for storing house data and creating message for the User
    """
    flat_area: float = 0.0
    rooms_number: int = 0
    floor: str = ''

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
