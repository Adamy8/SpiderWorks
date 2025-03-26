import scrapy
from bookscraper.items import BookItem
import random

class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    custom_settings = {         # this can be set to overwrite the settings.py file (not recommended)
        'FEEDS': {
            'bookdata.json': {'format': 'json', 'overwrite': True},
        },
    }

    user_agent_list = [        # copied from an online source
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/37.0.2062.94 Chrome/37.0.2062.94 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/8.0.8 Safari/600.8.9",
        "Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4",
        "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240",
        "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
        "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko",
        "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/8.0.7 Safari/600.7.12",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:40.0) Gecko/20100101 Firefox/40.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/7.1.8 Safari/537.85.17",
        "Mozilla/5.0 (iPad; CPU OS 8_4 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H143 Safari/600.1.4",
        "Mozilla/5.0 (iPad; CPU OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12F69 Safari/600.1.4",
    ]

    def parse(self, response):
        books = response.css("article.product_pod")
        for book in books:
            # yield {
            #     "title": book.css("h3 > a::text").get(),    # > means direct child
            #     "price": book.css(".product_price .price_color::text").get(),
            #     # "url" : book.css("h3 > a::attr(href)").get()
            #     "url" : book.css("h3 > a").attrib["href"],
            # }
            relative_url = book.css("h3 > a::attr(href)").get()
            if "catalogue/" in relative_url:
                book_url = "https://books.toscrape.com/" + relative_url
            else:
                book_url = "https://books.toscrape.com/catalogue/" + relative_url
            yield response.follow(book_url, callback=self.parse_book_page, headers={"User-Agent": self.user_agent_list[random.randint(0, len(self.user_agent_list) - 1) ]})

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            if "catalogue/" in next_page:
                next_page_url = "https://books.toscrape.com/" + next_page
            else:
                next_page_url = "https://books.toscrape.com/catalogue/" + next_page

            yield response.follow(next_page_url, callback=self.parse, headers={"User-Agent": self.user_agent_list[random.randint(0, len(self.user_agent_list) - 1) ]})

    def parse_book_page(self, response):
        table_rows = response.css("table tr")
        book_item = BookItem()
        
        book_item['url'] = response.url
        book_item['title'] = response.css(".product_main h1::text").get()
        book_item['upc'] = table_rows[0].css("td::text").get()
        book_item['product_type'] = table_rows[1].css("td::text").get()
        book_item['price_excl_tax'] = table_rows[2].css("td::text").get()
        book_item['price_incl_tax'] = table_rows[3].css("td::text").get()
        book_item['tax'] = table_rows[4].css("td::text").get()
        book_item['availability'] = table_rows[5].css("td::text").get()
        book_item['num_reviews'] = table_rows[6].css("td::text").get()
        book_item['stars'] = response.css("p.star-rating").attrib["class"]
        book_item['category'] = response.xpath("//ul[@class='breadcrumb']/li[3]/a/text()").get()
        book_item['description'] = response.xpath("//div[@id='product_description']/following-sibling::p/text()").get()
        book_item['price'] = response.css("p.price_color::text").get()
        
        yield book_item