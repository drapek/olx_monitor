import settings
from auction_page_parser import AuctionPageParser
from email_sender import EmailClient
from scrapper import Scrapper


def run_on_url():
    s = Scrapper()
    s.scan_site("https://www.olx.pl/warszawa/q-sylwester/?search%5Border%5D=created_at%3Adesc&search%5Bdist%5D=30", '')


def run_on_local_file():
    s = Scrapper()
    s.analyze_html_page(open("tests/example_page_2020.html", 'r').read())


def send_email():
    es = EmailClient()
    es.send_email(settings.EMAIL_USER, 'test', 'super <b>test</b> 2')


def debug_sprzedajemy_pl():
    url = 'https://sprzedajemy.pl/motoryzacja/samochody-osobowe/volvo/850'
    cookie = 'observed_id=188519212661547b94b17df2201910418615287190; G_ENABLED_IDPS=google; _items_per_page__offer_list=30; FRSPSID=9kjdimf60nen04vhfcfl507rd4; _gid=GA1.2.236234176.1633595206; __gfp_64b=A9960nqJNEBaXqI_f9BoH2OdZmoVlTQ2vh7oXg5K5pb.e7|1631695941; _ga_YN7BSR1T8G=GS1.1.1633627500.3.1.1633627548.12; _ga=GA1.2.379562157.1632926615; cto_bundle=d4_jMV9NaHBVektNS3ZKak1KOENPM2JWbDJpaVczMU1pekFsN3JRT2ZOanB5JTJGdCUyRiUyQkpBTG56cW5GNmFmTlRQUjRjM2ZZJTJCMHNtaEpJaXNGM01PJTJCWlp5MmlYb3RhaXg4RzhzRCUyQjhRNjZsODFNbE9ROGJUdVBIUlZMT2hXazhzdVp1WVp5Yld5VSUyRmNHQkM5bjFlR0RUOFFrJTJCVEp3JTNEJTNE'
    offers_dict = AuctionPageParser.scan_site(url, cookie)
    print(f'Found offers: {offers_dict}')


if __name__ == '__main__':
    # send_email()
    # run_on_local_file()
    debug_sprzedajemy_pl()
