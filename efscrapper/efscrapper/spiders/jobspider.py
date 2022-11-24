# -*- coding: utf-8 -*-
import os, sys, re, json, scrapy, csv

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from efscrapper.spiders.mainspider import MainSpider
from efscrapper.items.jobitem import JobItem
from efscrapper.util.constant import Constant
from datetime import datetime
import pandas as pd
import numpy as np


class JobSpider(MainSpider):
    name = Constant.JOB_SPIDER
    crawl_type = Constant.CRAWL_TYPE_JOB

    def __init__(self, config_name=None):
        MainSpider.__init__(self, config_name)

    def parse(self, response):
        # TODO
        if response.status in self.handle_httpstatus_list:
            return
        job_items = self.get_job_items(response)
        for job_item in job_items:
            # pass
            # yield job_item
            with open(self.filename, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                temp_list = []
                for key_i in self.columns:
                    temp_list.append(job_item[key_i])
                writer.writerow(temp_list)


    def get_job_items(self, response):
        obj_template = {"response": response,
                        "job_url": response.meta['start_url'],
                        }
        temp_obj = {}
        # print("temporary stock check: ", response.xpath('//a[contains(text(),"add to bag ")]/text()').extract())
        objs = []
        ext_codes_dict = self.ext_codes

        ordered_keys = self.return_ordered_ext_keys(ext_codes_dict)
        # print(ext_codes_dict)
        for key in ordered_keys:
            item_dict = ext_codes_dict[key]
            final_parsing_type = ext_codes_dict[key].get('parsing_type') or self.default_parsing_type

            # print("<------------------", key, "------------------>")
            if key == 'block':
                if final_parsing_type == 'xpath':
                    value = self.update_xpath(obj_template, key, item_dict)
                elif final_parsing_type == 'jpath':
                    value = self.update_jpath(obj_template, key, item_dict)
                obj_template[key] = value
        for k in obj_template:
            temp_obj[k] = obj_template[k]
        for key in ordered_keys:
            item_dict = ext_codes_dict[key]
            final_parsing_type = ext_codes_dict[key].get('parsing_type') or self.default_parsing_type
            if key != 'block':
                if final_parsing_type == 'xpath':
                    temp_obj[key] = self.update_xpath(temp_obj, key, item_dict)
                elif final_parsing_type == 'jpath':
                    temp_obj[key] = self.update_jpath(temp_obj, key, item_dict)
                if temp_obj[key] == temp_obj['response'].text:
                    temp_obj[key] = np.nan
                # print(key, " temp_obj[key]: ", temp_obj[key])
        objs.append(temp_obj)
        return self.generate_item(JobItem, objs)
