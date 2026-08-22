import requests
from bs4 import BeautifulSoup
import datetime
from collections import namedtuple
from jinja2 import Template
import sys
from pathlib import Path
sys.path.append(str(Path.home()/'py_script'/'email_func'))
import email_func




URL = 'http://omiai-dakimakura.com/page/'




Article = namedtuple('Article', ['title', 'date', 'thumbnail', 'link',])


class Page():
    def __init__(self, html: str | BeautifulSoup, page_number=None):
        if isinstance(html, str):
            html = BeautifulSoup(html, 'html5lib')

        self.page_number = page_number if page_number else html.find('nav', class_='pagination group').find('span', class_='current').string

        articles = html.find_all('article')
        self.dakis = [Article(
            title = str(article.find('h2', class_='post-title').a.string),
            date = datetime.datetime.strptime(article.find('p', class_='post-date').string, r'%Y年%m月%d日').date(),
            thumbnail = article.find('div', class_='post-thumbnail').img.get('src'), 
            link = article.find('h2', class_='post-title').a.get('href'),
        ) for article in articles]


    def __getitem__(self, position):
        return self.dakis[position]

    
    def __len__(self):
        return len(self.dakis)




def get_recent_dakis(past_days=0) -> list[Article]:
    """
    Return a list of dakimakura data. Each Article in the list represent a dakimakura released within the requested time range. Return an empty list if there're no matching results.
    """

    today = datetime.date.today()
    starting_from = today - datetime.timedelta(days=past_days)
    dakis = []
    page_number = 1

    while True:
        html = requests.get(URL+str(page_number), verify=False).content.decode()
        page = Page(html)

        for article in page: 
            if article.date < starting_from:
                return dakis
            dakis.append(article)

        page_number += 1


def notify_new_dakis(past_days=0) -> None:
    """
    Execute get_recent_dakis function and notify the user via sending email to them.
    """

    today = datetime.date.today()
    starting_from = today - datetime.timedelta(days=past_days)
    dakis = get_recent_dakis(past_days)
    
    if not dakis: 
        print('No matching results.')
        return 

    subject = f'New dakimakuras released on {today}' if starting_from == today else f'New dakimakuras released from {starting_from} to {today}'
    template = Template("""
    <html><body>
        {% for daki in dakis %}
            <a href='{{ daki[3] }}'><img src="{{ daki[2] }}" style='width:100%; max-width:400px; margin-bottom:10px;'></a><br>
        {% endfor %}
    </body></html>
    """)
    content = template.render(dakis=dakis)
    email_func.send_email(subject=subject, content=content, subtype='html')

    



if __name__ == '__main__':
    notify_new_dakis(past_days=0)