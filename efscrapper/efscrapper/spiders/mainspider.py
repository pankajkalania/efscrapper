# -*- coding: utf-8 -*-
import os, sys, re, json, scrapy, csv
from scrapy import signals
import requests
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from temp_configs.temp_config import site_config
from efscrapper.items.jobitem import JobItem
from scrapy.http import HtmlResponse
from functools import reduce
from datetime import datetime
import pandas as pd
import numpy as np

class MainSpider(scrapy.Spider):
    name = 'mainspider'
    handle_httpstatus_list = [307]

    def __init__(self, config_name=None):
        if config_name:
            self.directory = os.getcwd() + '/../raw_data/' + config_name.split("_")[0] + '/' + datetime.today().strftime('%Y-%m-%d')
            print("directory: ", self.directory)
            if not os.path.isdir(self.directory):
                print("Directory doesn't exists. So, creating one.")
                os.makedirs(self.directory)
            else:
                print("Directory already exists.")
            self.filename = self.directory + '/' + config_name.split("_")[0] + '_' + self.crawl_type + '.csv'
            self.columns = list(JobItem().fields)
            self.headers = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"}
            self.columns.sort()
            self.config_name = config_name
            self.config_dict = site_config[config_name]
            self.allowed_domains = self.config_dict['allowed_domains']
            self.vendor = self.config_dict['domain']
            self.start_urls = []
            if self.crawl_type == "category":
                self.start_urls = self.config_dict[self.crawl_type]['start_urls']
                with open(self.filename, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(('job_url', 'job_title'))
            if self.crawl_type == "job":
                try:
                    url_data = pd.read_csv(self.directory + '/' + config_name.split("_")[0] + '_' + 'category' + '.csv')
                except:
                    url_data = pd.read_csv(self.directory + '/' + config_name.split("_")[0] + '_' + 'sitemap' + '.csv')
                self.start_urls = list(url_data.iloc[59015:]['job_url'])

                with open(self.filename, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(self.columns)
                

            self.default_parsing_type = self.config_dict[self.crawl_type].get('parsing_type') or self.config_dict['parsing_type']
            self.ext_codes = self.config_dict[self.crawl_type]['ext_codes']
            self.pagination = self.config_dict[self.crawl_type].get('pagination') or None
            self.default_selector = 'response'

    def start_requests(self):
        for url in self.start_urls:
            temp_request_url = url
            if self.config_name == 'monsterindia_com':
                temp_request_url = "https://www.monsterindia.com/middleware/jobdetail/" + url.split("-")[-1]
            yield scrapy.Request(url=temp_request_url, callback=self.parse, method=self.config_dict['method'],
                                 meta={'start_url': url, 'pagination_url': url, 'input_values': {"gender"}})

    def parse(self, response):
        pass

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(MainSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
        return spider

    def spider_closed(self, spider):
        spider.logger.info('SSSSpider closed: %s', spider.name)

    def spider_opened(self, spider):
        spider.logger.info('SSSSpider opened: %s', spider.name)

    def exec_codes(self, temp_json_html, item_dict):
        temp_key_list = []
        final_selector = item_dict.get('selector') or self.default_selector
        final_parsing_type = item_dict.get('parsing_type') or self.default_parsing_type
        if 'paths' in item_dict:
            paths = item_dict['paths']
            if final_parsing_type == "jpath" and final_selector == "response":
                temp_json_html = json.loads((temp_json_html.text))
            for path in paths:
                if final_parsing_type == "jpath":
                    code_value = 'temp_key_list.extend(temp_json_html' + path + ' if type(temp_json_html'+ path +') == list else [temp_json_html'+ path +'])'
                    try:
                        exec (code_value)
                    except:
                        temp_key_list.extend([])
                else:
                    temp_key_list.extend(temp_json_html.xpath(path).extract())
        elif final_selector == 'response':
            temp_key_list.append(temp_json_html.text)
        else:
            temp_key_list.append(temp_json_html)
        return temp_key_list

    def apply_cleanup_func(self, obj, key, item_dict):
        return_key_values = []
        if 'cleanup_functions' in item_dict:
            cleanup_functions = item_dict['cleanup_functions']
            # obj[key] = eval(cleanup_functions[0])
            for key_i in range(len(obj[key])):
                for cleanup_function in cleanup_functions[:]:
                    try:
                        obj[key][key_i] = eval(cleanup_function)
                    except Exception as ex:
                        print("Could not apply: "+cleanup_function)
                        print(ex)
                        obj[key][key_i] = obj[key][key_i]
        return_key_values.extend(obj[key])
        return return_key_values

    def update_xpath(self, obj, key, item_dict):
        # print("update_xpath starts")
        final_selector = item_dict.get('selector') or self.default_selector
        key_values = self.exec_codes(obj[final_selector], item_dict)
        obj[key] = key_values
        processed_key_values = self.apply_cleanup_func(obj, key, item_dict)
        try:
            # if key != "iterable":
            #     print("mainspider test: ", self.return_value(item_dict['return_type'], processed_key_values))
            return self.return_value(item_dict, processed_key_values)
        except:
            return None

    def update_jpath(self, obj, key, item_dict):
        # print("update_jpath starts")
        # print("<------------------", key, "------------------>")
        final_selector = item_dict.get('selector') or self.default_selector
        # if key == 'iterable':
        #     print(len(obj[final_selector]))
        key_values = self.exec_codes(obj[final_selector], item_dict)
        obj[key] = key_values
        processed_key_values = self.apply_cleanup_func(obj, key, item_dict)
        try:
            return self.return_value(item_dict, processed_key_values)
        except:
            return None

    def return_value(self, item_dict, key_values):
        returntype = item_dict['return_type']
        if returntype == 'str':
            key_value = key_values[0]
            # key_value = key_value.decode('utf-8')
            key_value = str(key_value)
        elif returntype == 'htmlResponse':
            key_value = key_values[0]
        elif returntype == 'int':
            key_value = key_values[0]
            key_value = int(key_value)
        elif returntype == 'join':
            key_value = item_dict['join_str'].join(key_values)
        elif returntype == 'list':
            key_value = key_values
        elif returntype == '2Dlist':
            key_value = reduce(lambda x, y: x+y, key_values)
        elif returntype == 'json':
            key_value = json.loads(key_values[0])
        return key_value

    def generate_item(self, item_class, objs):
        item_objs=[]
        for obj_i in objs:
            item = item_class()
            for field in item.fields:
                item[field] = obj_i.get(field)
            item_objs.append(item)
        return item_objs

    def return_ordered_ext_keys(self, ext_codes):
        output_ext_key_order = []
        if 'block' in ext_codes.keys():
            output_ext_key_order.append('block')
        if 'block1' in ext_codes.keys():
            output_ext_key_order.append('block1')
        if 'iterable' in ext_codes.keys():
            output_ext_key_order.append('iterable')
        for key in ext_codes.keys():
            if key not in output_ext_key_order:
                output_ext_key_order.append(key)
        return output_ext_key_order

