from datetime import datetime

import settings
from data_classes.house import HouseOffer
from email_sender import EmailClient
from logger import log_print
from messenger_client import MessengerClient


class MessageSender:
    messenger_client = None
    email_client = None
    RECIPIENT_EMAILS = []

    def __init__(self, recipient_emails):
        self._init_clients()
        self.RECIPIENT_EMAILS = recipient_emails

    def _init_clients(self):
        client_available = False
        if settings.MESSENGER_APP_TOKEN and settings.MESSENGER_RECIPIENTS:
            self.messenger_client = MessengerClient(settings.MESSENGER_APP_TOKEN, settings.MESSENGER_RECIPIENTS)
            client_available = True

        if settings.EMAIL_USER and settings.EMAIL_PASSWORD:
            self.email_client = EmailClient()
            client_available = True

        if not client_available:
            log_print('[WARRNING] No message client are available! Email and messenger won\'t be send.', message_type=1)

    def send_messages(self, offer):
        self._send_email(offer)
        self._send_messenger_msg(offer)

    def _send_email(self, offer: HouseOffer) -> None:
        if self.email_client:
            email_body = f'<!DOCTYPE html>' \
                         f'<html lang="pl"><body>' \
                         f'{offer.message_body_html()}' \
                         f'</body></html>'

            self.email_client.send_email(self.RECIPIENT_EMAILS, "Drapek wyszukiwacz - nowe ogłoszenie na OLX", email_body)

    def _send_messenger_msg(self, offer: HouseOffer) -> None:
        if self.messenger_client:
            if offer.image_url:
                self.messenger_client.send_image(offer.image_url)
            self.messenger_client.send_message(offer.message_body_messenger())


if __name__ == '__main__':
    ms = MessageSender([])
    offer = HouseOffer(id='olx_234', tittle='Title 123', price=600000, flat_area=53.3, rooms_number=3,
                       image_url='https://ireland.apollo.olxcdn.com/v1/files/eyJmbiI6ImJzcDJ6YmpkZnhoNzMtQVBMIiwidyI6W3siZm4iOiJlbnZmcXFlMWF5NGsxLUFQTCIsInMiOiIxNCIsInAiOiIxMCwtMTAiLCJhIjoiMCJ9XX0.0gAHYYs5lxlpwfzyXnunh3rx_Uv4doinP94h_PHNNhk/image;s=655x491;q=80',
                       offer_url='https://olx.pl/offer/1234',
                       add_date=datetime(2021, 11, 11, 15, 45), localization='Wola, Góreczewska 128')
    ms._send_messenger_msg(offer)

