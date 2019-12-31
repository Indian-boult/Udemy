import scrapy
from scrapy.http import Request
import bs4 as bs
import pandas as pd

class UdemySpider(scrapy.Spider):
    name = 'udemy'
    start_urls = [pd.read_csv("/Users/thai/Desktop/Kris/out/Algebra.csv")['URL']]

    def __init__(self, category=None, *args, **kwargs):
        super(UdemySpider, self).__init__(*args, **kwargs)

        new_cols = ['Category 1', 'Category 2', 'Category 3', 
                    'Enrollment', 'Language', 'Description',
                     'Last Update', 'Date Scraped']

        df = pd.read_csv("/Users/thai/Desktop/Kris/out/Algebra.csv")
        self.start_urls = list(df['URL'])

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url='https://' + url, callback=self.parse_data, dont_filter=True)

    def parse_data(self, response):
        html = response.body
        return self.scrape_html(response.body, "12/31/19")
        

    def scrape_html(self, html, date_scraped):
        new_cols = ['Category 1', 'Category 2', 'Category 3', 'Enrollment', 'Language', 'Description', 'Last Update', 'Date Scraped']
        soup = bs.BeautifulSoup(html, 'lxml')
        private = soup.find('div', attrs = {'class':'col-sm-4 col-sm-push-4 col-xs-8 col-xs-push-2'})
        private_2 = soup.find('i', attrs = {'class': 'udi udi-warning'})

        if (private is not None) or (private_2 is not None):
            print("private")
            none = ["None"] * len(new_cols)
            return dict(zip(new_cols,none))

        enrollment = soup.find('div', attrs = {'data-purpose' : 'enrollment'})
        last_update = soup.find('div', attrs = {'class': 'last-update-date'})
        language = soup.find('div', attrs = {'class': 'clp-lead__locale'})
        description = soup.find('div', attrs = {'class' : 'clp-lead__headline'})
        categories = [cat.text.strip("\n") for cat in soup.find_all('a', attrs = {'class': 'topic-menu__link'})]

        try:
            cat = [" ", " ", " "]
            for idx in range(len(categories)):
                cat[idx] = categories[idx]

            data = [cat[0], cat[1], cat[2], enrollment.text.strip(" \n").split(" ")[0],
                    language.text.strip("\n"), description.text.strip("\n"),
                    last_update.text.strip("\n").split(" ")[-1], date_scraped]

            data_dict = dict(zip(new_cols,data))
            return data_dict
        except Exception:
            raise Exception()
