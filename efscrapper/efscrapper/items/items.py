# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class EfscrapperItem(scrapy.Item):
    job_url = scrapy.Field()
    job_title = scrapy.Field()
    job_description = scrapy.Field()
    job_experience_required = scrapy.Field()
    job_education_required = scrapy.Field()
    job_location = scrapy.Field()
    job_date_posted = scrapy.Field()
    job_valid_through = scrapy.Field()
    job_key = scrapy.Field()
    similar_job_keys = scrapy.Field()
    job_work_hour = scrapy.Field()
    job_salary = scrapy.Field()
    job_type = scrapy.Field()
    job_industry_type = scrapy.Field()
    job_profile = scrapy.Field()
    job_key_skills = scrapy.Field()
    job_views = scrapy.Field()
    job_applicants = scrapy.Field()
    job_openings = scrapy.Field()
    company_name = scrapy.Field()
    about_company = scrapy.Field()
    company_url = scrapy.Field()
    company_website = scrapy.Field()
    company_rating = scrapy.Field()
    company_number_of_reviews = scrapy.Field()
    company_turn_over = scrapy.Field()
    company_size = scrapy.Field()
    contact_person_name = scrapy.Field()
    contact_person_email = scrapy.Field()
    contact_person_number = scrapy.Field()
    timestamp = scrapy.Field()

   
#derived fields ---> gender, category and stock
