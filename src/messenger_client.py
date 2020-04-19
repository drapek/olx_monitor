import requests

import settings
from logger import log_print


class MessengerClient:
    ENDPOINT_SEND_MSG = 'https://graph.facebook.com/v6.0/me/messages?access_token={token}'

    def __init__(self, app_token, recipients):
        self.token = app_token
        self.recipients_ids = recipients

    def send_message(self, message):
        self._send_request(message, self._generate_message_request)

    def send_image(self, image_url):
        self._send_request(image_url, self._generate_image_request)

    def _send_request(self, data, request_body_generator):
        for recipient in self.recipients_ids:
            try:
                request_body = request_body_generator(recipient, data)
                resp = requests.post(self.ENDPOINT_SEND_MSG.format(token=self.token),
                                     json=request_body)
                log_print(f'Sending POST {request_body} to API messenger')
                if resp.status_code != 200:
                    raise ConnectionError(f"Can't fetch data. {resp.status_code} : {resp.content}")
            except Exception as e:
                log_print(f"Coudn't send message via Messneger to {recipient}. The error: {e}", message_type=1)

    def _generate_message_request(self, recipient_id, message):
        request_body = {
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "text": message
            }
        }
        return request_body

    def _generate_image_request(self, recipient_id, image_url):
        request_body = {
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "attachment": {
                    'type': 'image',
                    'payload': {
                        'is_reusable': True,
                        'url': image_url
                    }
                }
            }
        }
        return request_body


if __name__ == '__main__':
    mc = MessengerClient(settings.MESSENGER_APP_TOKEN, ['2859498154143240'])
    mc.send_message('Debug message to see if sending works')
