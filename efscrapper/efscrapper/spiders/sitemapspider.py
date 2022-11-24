import os, sys, re, json, scrapy
from efscrapper.spiders.mainspider import MainSpider
from efscrapper.util.constant import Constant
from scrapy.http import HtmlResponse
from efscrapper.items.categoryitem import CategoryItem
from scrapy.spiders import CrawlSpider, Rule
from temp_configs.temp_config import site_config
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import SitemapSpider
from scrapy.utils.sitemap import Sitemap, sitemap_urls_from_robots
from scrapy.http import Request, XmlResponse
import logging
import csv
import numpy as np
import pandas as pd
from datetime import datetime
logger = logging.getLogger(__name__)


class GenericSitemapSpider(SitemapSpider):
    name = Constant.SITEMAP_SPIDER
    crawl_type = Constant.CRAWL_TYPE_SITEMAP

    def __init__(self, config_name=None):

        if config_name:
            self.config_name = config_name
            self.config_dict = site_config[config_name]
            self.start_urls = self.config_dict[self.crawl_type]['start_urls']
            self.sitemap_urls = self.start_urls
            self.sitemap_rules = [(r, 'parse') for r in self.config_dict[self.crawl_type]['sitemap_rules']]
            if self.config_dict[self.crawl_type].get('sitemap_follow'):
                self.sitemap_follow = self.config_dict[self.crawl_type]['sitemap_follow']
            # print(self.sitemap_rules)
            self.directory = os.getcwd() + '/../raw_data/' + config_name.split("_")[0] + '/' + datetime.today().strftime(
                '%Y-%m-%d')
            print("directory: ", self.directory)
            if not os.path.isdir(self.directory):
                print("Directory doesn't exists. So, creating one.")
                os.makedirs(self.directory)
            else:
                print("Directory already exists.")
            self.filename = self.directory + '/' + config_name.split("_")[0] + '_' + self.crawl_type + '.csv'
            with open(self.filename, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(('job_url', 'job_title'))

        super(GenericSitemapSpider, self).__init__()

    def sitemap_filter(self, entries):
        for entry in entries:
            # print("entry: ", entry)
            yield entry
            # pass

    def _parse_sitemap(self, response):
        if response.url.endswith('/robots.txt'):
            for url in sitemap_urls_from_robots(response.text, base_url=response.url):
                yield Request(url, callback=self._parse_sitemap)
        else:
            body = self._get_sitemap_body(response)
            if body is None:
                logger.warning("Ignoring invalid sitemap: %(response)s",
                               {'response': response}, extra={'spider': self})
                return

            s = Sitemap(body)
            it = self.sitemap_filter(s)

            if s.type == 'sitemapindex':
                for loc in iterloc(it, self.sitemap_alternate_links):
                    if any(x.search(loc) for x in self._follow):
                        yield Request(loc, callback=self._parse_sitemap)
            elif s.type == 'urlset':
                for loc in iterloc(it, self.sitemap_alternate_links):
                    for r, c in self._cbs:
                        if r.search(loc):
                            item = CategoryItem()
                            item['job_url'] = loc
                            # print(item)
                            with open(self.filename, 'a') as f:
                                writer = csv.writer(f)
                                writer.writerow([item['job_url'], np.nan])
                            # yield Request(loc, callback=c)
                            break

    def parse(self, response):
        pass


def iterloc(it, alt=False):
    for d in it:
        yield d['loc']

        # Also consider alternate URLs (xhtml:link rel="alternate")
        if alt and 'alternate' in d:
            for l in d['alternate']:
                yield l
