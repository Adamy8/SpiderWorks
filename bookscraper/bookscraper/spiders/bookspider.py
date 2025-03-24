import scrapy

class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response):
        books = response.css("article.product_pod")
        for book in books:
            # yield {
            #     "title": book.css("h3 > a::text").get(),    # > means direct child
            #     "price": book.css(".product_price .price_color::text").get(),
            #     # "url" : book.css("h3 > a::attr(href)").get()
            #     "url" : book.css("h3 > a").attrib["href"],
            # }
            relative_url = book.css("h3 > a::attri(href)").get()
            if "catalogue/" in relative_url:
                book_url = "https://books.toscrape.com/" + relative_url
            else:
                book_url = "https://books.toscrape.com/catalogue/" + relative_url
            yield response.follow(book_url, callback=self.parse_book_page)

        next_page = response.css("li.next > a::attr(href)").get()
        if next_page:
            if "catalogue/" in next_page:
                next_page_url = "https://books.toscrape.com/" + next_page
            else:
                next_page_url = "https://books.toscrape.com/catalogue/" + next_page

            yield response.follow(next_page_url, callback=self.parse)

    def parse_book_page(self, response):
        pass