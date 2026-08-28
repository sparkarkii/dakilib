import requests
from bs4 import BeautifulSoup
import datetime
from collections import namedtuple
from jinja2 import Template
from utils import emailfunc



URL = 'http://omiai-dakimakura.com/page/'




Daki = namedtuple('Daki', ['title', 'date', 'thumbnail', 'link',])




def get_recent_dakis(starting_from: datetime.date) -> list[Daki]:
    """
    Return a list of dakimakuras released after the date specified. Return an empty list if no items are found.
    """

    dakis = []
    page_number = 1

    while True:
        html = requests.get(URL+str(page_number), verify=False).content.decode()
        articles = BeautifulSoup(html, 'html5lib').find_all('article')
        page = []
        for article in articles:
            title = str(article.find('h2', class_='post-title').a.string)
            date = datetime.datetime.strptime(article.find('p', class_='post-date').string, r'%Y年%m月%d日').date()
            thumbnail = article.find('div', class_='post-thumbnail').img.get('src')
            link = article.find('h2', class_='post-title').a.get('href')
            page.append(Daki(title, date, thumbnail, link))

        for daki in page: 
            if daki.date < starting_from:
                return dakis
            dakis.append(daki)

        page_number += 1


def notify_new_dakis(starting_from: datetime.date) -> None:
    """
    Run get_recent_dakis and notify the user via email.
    """

    today = datetime.date.today()
    dakis = get_recent_dakis(starting_from)

    template = Template("""
    <html><body>
        {% for daki in dakis %}
            <a href='{{ daki[3] }}'><img src="{{ daki[2] }}" style='width:100%; max-width:400px; margin-bottom:10px;'></a><br>
        {% endfor %}
    </body></html>
    """)
    # subject = f'New dakimakuras released on {today}' if starting_from == today else f'New dakimakuras released from {starting_from} to {today}'
    subject = datetime.datetime.now()
    content = template.render(dakis=dakis) if dakis else 'No items found.'
    emailfunc.send_email(subject=subject, content=content, subtype='html')

    



if __name__ == '__main__':
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    notify_new_dakis(starting_from=yesterday)
