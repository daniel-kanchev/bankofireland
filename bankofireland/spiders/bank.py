import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bankofireland.items import Article


class BankSpider(scrapy.Spider):
    name = 'bank'
    start_urls = ['https://www.bankofireland.com/about-bank-of-ireland/press-room/press-releases/']

    def parse(self, response):

        articles = response.xpath('//table/tbody/*[td[@width="15%"]]')
        for article in articles:
            link = article.xpath('.//a/@href').get()
            date = article.xpath('.//td[@width="15%"]/text()').get()
            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

    def parse_article(self, response, date):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        if date:
            date = datetime.strptime(date.strip(), '%d %b %Y')
            date = date.strftime('%Y/%m/%d')

        content = response.xpath('//div[@class="mainContent__body"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[1:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
