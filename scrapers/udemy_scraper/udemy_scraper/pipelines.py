# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pandas as pd

class UdemyScraperPipeline(object):
    def __init__(self):
        new_cols = ['Category 1', 'Category 2', 'Category 3', 
                    'Enrollment', 'Language', 'Description',
                     'Last Update', 'Date Scraped']

        self.df = pd.DataFrame(columns=new_cols)


        def process_item(self, item, spider):
            self.df = self.df.append(item, ignore_index=True)
            print(self.df)
            return self.df
