from dataclasses import dataclass

from data_classes.base import BaseOffer


@dataclass(frozen=True)
class CarOffer(BaseOffer):
    """
    Class for storing Car data and creating message for the User
    """
    engine_size: str = ''
    mileage_in_km: str = ''
    gas_type: str = ''
    horse_power: int = 0

    def message_body_messenger(self) -> str:
        return ('Cześć znalazłem nowe ogłoszenie! \n\n '
                f'{self.tittle} \n\n'
                f'Silnik: {self.generate_engine_desc()} \n'
                f'Przebieg: {self.mileage_in_km} \n'
                f'Cena: {self.price} \n'
                f'Lokalizacja: {self.localization} \n'
                f'Dodano: {self.add_date} \n'
                f'Link: {self.offer_url}')

    def message_body_html(self) -> str:
        return (f'<b>Cześć, znanazłem nowe ogłoszenie! </b><h1>{self.tittle}</h1> '
                f'<table><tr><td><img src="{self.image_url}" /></td></tr>'
                f'<tr><td><b>Cena: {self.price}</b></td></tr>'
                f'<tr><td><p>Data dodania: {self.add_date}</p></td></tr>'
                f'<tr><td><p>Lokalizajca: {self.localization}</p></td></tr></table>'
                f'<a href="{self.offer_url}">Link do aukcji</a>')

    def generate_engine_desc(self) -> str:
        return f'{self.gas_type} {self.engine_size} {self.horse_power} HP'
