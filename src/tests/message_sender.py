import settings
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

    def send_messages(self, offer_data):
        self._send_email(offer_data)
        self._send_messenger_msg(offer_data)

    def _send_email(self, offer_data):
        if self.email_client:
            email_body = f'<!DOCTYPE html>' \
                         f'<html lang="pl"><body>' \
                         f'<b>Cześć, znanazłem nowe ogłoszenie! </b><h1>{offer_data["title"]}</h1> ' \
                         f'<table><tr><td><img src="{offer_data["image_url"]}" /></td></tr>' \
                         f'<tr><td><b>Cena: {offer_data["price"]}</b></td></tr>' \
                         f'<tr><td><p>Data dodania: {offer_data["add_time"]}</p></td></tr>' \
                         f'<tr><td><p>Lokalizajca: {offer_data["localization"]}</p></td></tr></table>' \
                         f'<a href="{offer_data["offer_url"]}">Link do aukcji</a>' \
                         f'</body></html>'

            self.email_client.send_email(self.RECIPIENT_EMAILS, "Drapek wyszukiwacz - nowe ogłoszenie na OLX", email_body)

    def _send_messenger_msg(self, offer_data):
        if self.messenger_client:
            message = f'Cześć znalazłem nowe ogłoszenie! \n\n' \
                      f'{offer_data["title"]}. \n\n' \
                      f'Cena: {offer_data["price"]} \n' \
                      f'Lokalizacja: {offer_data["localization"]} \n' \
                      f'Dodano {offer_data["add_time"]}. \n' \
                      f'Link {offer_data["offer_url"]}'
            self.messenger_client.send_image(offer_data["image_url"])
            self.messenger_client.send_message(message)

