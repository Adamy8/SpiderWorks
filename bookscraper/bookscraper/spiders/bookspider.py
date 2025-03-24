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
            relative_url = book.css("h3 > a::attr(href)").get()
            if "catalogue/" in relative_url:
                book_url = "https://books.toscrape.com/" + relative_url
            else:
                book_url = "https://books.toscrape.com/catalogue/" + relative_url
            yield response.follow(book_url, callback=self.parse_book_page)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            if "catalogue/" in next_page:
                next_page_url = "https://books.toscrape.com/" + next_page
            else:
                next_page_url = "https://books.toscrape.com/catalogue/" + next_page

            yield response.follow(next_page_url, callback=self.parse)

    def parse_book_page(self, response):
        table_rows = response.css("table tr")

        yield {
            'url' : response.url,
            'title' : response.css(".product_main h1::text").get(),
            "product_type" : table_rows[1].css("td::text").get(),
            "price_excl_tax" : table_rows[2].css("td::text").get(),
            "price_incl_tax" : table_rows[3].css("td::text").get(),
            "tax" : table_rows[4].css("td::text").get(),
            "availability" : table_rows[5].css("td::text").get(),
            "num_reviews" : table_rows[6].css("td::text").get(),
            'stars' : response.css("p.star-rating").attrib["class"],
            # 'category' : response.css(".breadcrumb li:nth-child(3) > a::text").get(),
            'category' : response.xpath("//ul[@class='breadcrumb']/li[3]/a/text()").get(),
            'description' : response.xpath("//div[@id='product_description']/following-sibling::p/text()").get(),
            'price' : response.css("p.price_color::text").get(),
        }