from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class BaseOffer(ABC):
    """
    The base class for the Data class with the offer
    """
    id: str
    portal_offer_id: str = ''
    tittle: str = ''
    price: float = 0.0
    image_url: str = ''
    offer_url: str = ''
    add_date: datetime = None
    localization: str = ''

    @abstractmethod
    def message_body_messenger(self) -> str:
        """
        Body of the message that will be send to the Messenger
        :return: String - message with the offer details
        """
        ...

    @abstractmethod
    def message_body_html(self):
        """
        Body of the message that will be send to the email
        :return: String - message with the offer details
        """
        ...
