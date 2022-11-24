# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from efscrapper.items.items import EfscrapperItem

class CategoryItem(EfscrapperItem):
    category_url = scrapy.Field()
    pagination_url = scrapy.Field()
