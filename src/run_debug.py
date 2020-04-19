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
    es.send_email('drapek39@gmail.com', 'test', 'super <b>test</b> 2')


if __name__ == '__main__':
    send_email()
    # run_on_local_file()
