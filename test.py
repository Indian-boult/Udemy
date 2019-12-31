import scrapy
from scrapy_splash import SplashRequest

class MySpider(scrapy.Spider):
    name = "spidey"
    start_urls = ["https://www.udemy.com/topic/investing/?p=1"]

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse,
                endpoint='render.html',
                args={'wait': 0.5},
            )

    def parse(self, response):
		print reponse

