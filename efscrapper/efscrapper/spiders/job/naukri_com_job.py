# -*- coding: utf-8 -*-
import os, sys, re, json, scrapy

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from efscrapper.spiders.categoryspider import CategorySpider
from efscrapper.spiders.jobspider import JobSpider
from efscrapper.items.jobitem import JobItem
from efscrapper.items.categoryitem import CategoryItem
from efscrapper.util.constant import Constant
from scrapy.http import HtmlResponse


class JobSpider(JobSpider):
    name = str(os.path.basename(__file__)).split('.')[0]
    crawl_type = Constant.CRAWL_TYPE_JOB

    def parse(self, response):
        user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"
        headers = {"User-Agent": user_agent,
                   "AppId": "121",
                   "SystemId": "Naukri"}
        start_url = response.meta['start_url']
        job_id = start_url.split("?")[0].split("-")[-1]
        request_url = "https://www.naukri.com/jobapi/v3/job/" + job_id
        temp_meta = {'start_url': response.meta["start_url"],
                     'request_url': request_url}

        yield scrapy.Request(request_url, callback=self.parse_naukri_response, headers=headers, meta=temp_meta)

    def parse_naukri_response(self, response):
        job_items = self.get_job_items(response)
        for job_item in job_items:
            job_item['job_url'] = response.meta['start_url']
            yield job_item
