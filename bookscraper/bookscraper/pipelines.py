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
        field_names - adapter.field_name()
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
