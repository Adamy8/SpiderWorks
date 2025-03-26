# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class BookscraperPipeline:
    def process_item(self, item, spider):
        
        adapter = ItemAdapter(item)

        # strip all whitespaces from strings
        field_names = adapter.field_names()
        for field_name in field_names:
            if field_name != 'description':
                value = adapter.get(field_name)
                adapter[field_name] = value.strip()

        # Catagory & Product Type -> lowercase
        lowercase_keys = ['category', 'product_type']
        for key in lowercase_keys:
            value = adapter.get(key)
            adapter[key] = value.lower()
 
        # Price -> float
        price_keys = ['price', 'price_excl_tax', 'price_incl_tax', 'tax']
        for key in price_keys:
            value = adapter.get(key)
            value = value.replace('£', '')  # = value.strip('£')
            adapter[key] = float(value)

        # Availability -> int
        availability_string = adapter.get('availability')
        split_string = availability_string.split("(")
        if len(split_string) < 2:
            adapter['availability'] = 0
        else:
            availability = split_string[1].split(' ')[0]
            adapter['availability'] = int(availability)

        # Num Reviews -> int
        num_reviews = adapter.get('num_reviews')
        adapter['num_reviews'] = int(num_reviews)

        # Stars -> int
        stars_string = adapter.get('stars')
        stars_text = stars_string.split(' ')[1].lower()
        if stars_text == 'zero':
            adapter['stars'] = 0
        elif stars_text == 'one':
            adapter['stars'] = 1
        elif stars_text == 'two':
            adapter['stars'] = 2
        elif stars_text == 'three':
            adapter['stars'] = 3
        elif stars_text == 'four':
            adapter['stars'] = 4
        elif stars_text == 'five':
            adapter['stars'] = 5

        return item


# save to MySQL
from dotenv import load_dotenv
import os
import mysql.connector

class SaveToMySQLPipeline:
    def __init__(self):
        load_dotenv()

        self.conn = mysql.connector.connect(
            host= os.getenv('MYSQL_HOST'),
            user= os.getenv('MYSQL_USER'),
            password= os.getenv('MYSQL_PASSWORD'),
            database= os.getenv('MYSQL_DATABASE'),
        )
        # create cursor to execute queries
        self.cursor = self.conn.cursor()
        # create table if none exists
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                id int NOT NULL auto_increment,
                url VARCHAR(255),
                title text,
                upc VARCHAR(255),
                product_type VARCHAR(255),
                price_excl_tax DECIMAL,
                price_incl_tax DECIMAL,
                tax DECIMAL,
                price DECIMAL,
                availability INT,
                num_reviews INT,
                stars INT,
                category VARCHAR(255),
                description text,
                PRIMARY KEY (id)
            )
            """
        )

    def process_item(self, item, spider):

        ## Define insert statement
        self.cursor.execute(""" insert into books (
            url, 
            title, 
            upc, 
            product_type, 
            price_excl_tax,
            price_incl_tax,
            tax,
            price,
            availability,
            num_reviews,
            stars,
            category,
            description
            ) values (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
                )""", (
            item["url"],
            item["title"],
            item["upc"],
            item["product_type"],
            item["price_excl_tax"],
            item["price_incl_tax"],
            item["tax"],
            item["price"],
            item["availability"],
            item["num_reviews"],
            item["stars"],
            item["category"],
            str(item["description"][0])
        ))

        # ## Execute insert of data into database
        self.conn.commit()
        return item

        
    def close_spider(self, spider):

        ## Close cursor & connection to database 
        self.cursor.close()
        self.conn.close()