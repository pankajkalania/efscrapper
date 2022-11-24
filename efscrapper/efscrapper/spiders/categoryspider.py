# -*- coding: utf-8 -*-
import os, sys, re, json, scrapy, csv

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from efscrapper.spiders.mainspider import MainSpider
from efscrapper.items.categoryitem import CategoryItem
from efscrapper.util.constant import Constant
from scrapy.http import HtmlResponse
import math

class CategorySpider(MainSpider):
    name = Constant.CATEGORY_SPIDER
    crawl_type = Constant.CRAWL_TYPE_CATEGORY

    def parse(self, response):
        if response.status in self.handle_httpstatus_list:
            # TODO - logic to retry
            return
        category_items = self.get_category_items(response)
        for category_item in category_items:
            # yield category_item
            with open(self.filename, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([category_item['job_url'], category_item['job_title']])
            # pass
        temp_meta = self.apply_pagination(response)
        if temp_meta['pagination_url']:
            yield scrapy.Request(url=temp_meta.get('pagination_url'), callback=self.parse, meta=temp_meta)

    def apply_pagination(self, response):
        temp_meta = None
        if self.pagination:
            pagination_type = self.pagination['type']
            if pagination_type == 'FOLLOW_LINKS':
                obj_template = {'response': response}
                pagination_dict = self.pagination['next_page_criteria']['ext_codes']
                next_page_url = self.update_xpath(obj_template, 'next_url', pagination_dict)
                temp_meta = {'start_url': response.meta["start_url"],
                             'pagination_url': next_page_url}
            elif pagination_type == 'REPLACE_URL':
                total_pages = None
                if self.pagination.get('stop_criteria').get('ext_codes'):
                    if not response.meta.get("total_pages"):
                        print("total_pages doesn't exists. So calculating them.")
                        pagination_ext_codes = self.pagination.get('stop_criteria').get('ext_codes')
                        obj_template = {'response': response}
                        print("temp test: ", response.xpath('//div[contains(text()," products")]/text()'))
                        for key in self.return_ordered_ext_keys(pagination_ext_codes):
                            if pagination_ext_codes[key]['parsing_type'] == 'jpath':
                                value = self.update_jpath(obj_template, key, pagination_ext_codes[key])
                            elif pagination_ext_codes[key]['parsing_type'] == 'xpath':
                                value = self.update_xpath(obj_template, key, pagination_ext_codes[key])
                            obj_template[key] = value
                        if obj_template.get("total_pages"):
                            total_pages = obj_template["total_pages"]
                        else:
                            total_pages = float(obj_template["total_results"]) / float(
                                self.pagination['next_page_criteria']['total_product_per_page'])
                            total_pages = math.ceil(total_pages)
                        print("total_pages calculated are: ", total_pages)
                total_pages = response.meta.get("total_pages") or total_pages
                print("total_pages: ", total_pages)
                start_page_index = self.pagination['next_page_criteria']['start_page']
                diff_page_index = int(self.pagination['next_page_criteria']['diff_index'])
                if self.pagination['next_page_criteria']['page_text'] in response.meta['pagination_url']:
                    temp_page_url = response.meta['pagination_url']
                else:
                    temp_page_url = response.meta['pagination_url'] + self.pagination['next_page_criteria']['page_text'] + str(
                        start_page_index)
                current_page = response.meta.get('current_page', 1)
                # print("current_page: ", current_page)
                # print("total_pages: ", total_pages)
                if self.pagination.get('stop_criteria').get('stoping_logic'):
                    # print("stoping_logic exists")
                    if eval(self.pagination['stop_criteria']['stoping_logic']):
                        print("should break")
                        temp_meta = {'start_url': response.meta["start_url"],
                                     'total_pages': total_pages,
                                     'current_page': current_page + 1,
                                     'pagination_url': None}
                        return temp_meta
                elif current_page >= total_pages:
                    # print("should break")
                    temp_meta = {'start_url': response.meta["start_url"],
                                 'total_pages': total_pages,
                                 'current_page': current_page + 1,
                                 'pagination_url': None}
                    return temp_meta
                temp_replace_text = self.pagination['next_page_criteria']['page_text'] + str(
                    start_page_index + diff_page_index*(current_page-1))
                temp_replace_with_text = self.pagination['next_page_criteria']['replace_with'] + str(
                    start_page_index + diff_page_index*(current_page))
                next_page_url = temp_page_url.replace(temp_replace_text, temp_replace_with_text)
                temp_meta = {'start_url': response.meta["start_url"],
                             'total_pages': total_pages,
                             'current_page': current_page + 1,
                             'pagination_url': next_page_url}
        return temp_meta

    def get_category_items(self, response):
        # print("response.url: ", response.url)
        # print("headers: ", response.request.headers)
        # temp_response_file_paths = "/home/pankaj/Charmboard/scraping/cbscrapper/cbscrapper/clubfactory_category_responses/"
        # with open(temp_response_file_paths + "response"+str(re.findall("\d+", response.url)[2])+".txt", "w") as text_file:
        #     text_file.write(response.text)
        obj_template = {'response': response}
        objs = []
        ext_codes_dict = self.ext_codes
        ordered_keys = self.return_ordered_ext_keys(ext_codes_dict)
        for key in ordered_keys:
            # print("<------------------", key, "------------------>")
            if key == 'block' or key == 'block1':
                item_dict = ext_codes_dict[key]
                final_parsing_type = ext_codes_dict[key].get('parsing_type') or self.default_parsing_type
                if final_parsing_type == 'xpath':
                    value = self.update_xpath(obj_template, key, item_dict)
                elif final_parsing_type == 'jpath':
                    value = self.update_jpath(obj_template, key, item_dict)
                obj_template[key] = value

            elif key == 'iterable':
                item_dict = ext_codes_dict[key]
                final_parsing_type = ext_codes_dict[key].get('parsing_type') or self.default_parsing_type
                iterator_values = []
                # if 'paths' not in list(item_dict.keys()):
                #     iterator_values =
                if final_parsing_type == 'xpath':
                    value = self.update_xpath(obj_template, key, item_dict)
                    for v in value:
                        iterator_values.append(HtmlResponse(url="html string", body=v, encoding='utf-8'))
                elif final_parsing_type == 'jpath':
                    iterator_values = self.update_jpath(obj_template, key, item_dict)
                print("length of iterator_values: ", len(iterator_values))
                for iter_i in iterator_values:
                    temp_obj = {}
                    for k in obj_template:
                        temp_obj[k] = obj_template[k]
                    temp_obj['iterable'] = iter_i
                    objs.append(temp_obj)

            else:
                item_dict = ext_codes_dict[key]
                final_parsing_type = ext_codes_dict[key].get('parsing_type') or self.default_parsing_type
                # print("length of objs: ", len(objs))
                for obj in objs:
                    if final_parsing_type == 'xpath':
                        value = self.update_xpath(obj, key, item_dict)
                    elif final_parsing_type == 'jpath':
                        value = self.update_jpath(obj, key, item_dict)
                    obj[key] = value
                    # if key == 'product_url':
                    #     print("product_url: ", obj['product_url'])

        return self.generate_item(CategoryItem, objs)



