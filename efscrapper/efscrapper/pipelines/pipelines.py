# -*- coding: utf-8 -*-

import csv
from efscrapper.items.categoryitem import CategoryItem
from efscrapper.items.jobitem import JobItem
import os
import sys
import logging
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class EfscrapperPipeline(object):
    def process_item(self, item, spider):
        return item
