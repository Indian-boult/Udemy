#!/usr/bin/env python

'''
level 1 & 2 scrape
'''

import time 
import shadow_useragent
import copy
import sys
import glob
import os
import re
import threading
import random
import bs4 as bs
import pandas as pd
from fake_useragent import UserAgent
from urllib2 import urlopen, Request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.options import DesiredCapabilities
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import warnings
warnings.filterwarnings("ignore")

get_ipython().system('/Users/thai/anaconda2/lib/python2.7/site-packages/shadow_useragent/getpk.sh')

ua = shadow_useragent.ShadowUserAgent()

PROXY = "104.156.247.181:8080"

def build_driver(user_agent):
    options = webdriver.ChromeOptions()
    PROXY = "45.32.231.36:31280"
    
    options.add_argument("--incognito")
#     options.add_argument("--headless")
    prefs = {'profile.managed_default_content_settings.images':2, 'disk-cache-size': 4096}
    options.add_experimental_option("prefs", prefs)
    options.add_argument('--proxy-server=%s' % PROXY)
    options.binary_location = '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser'
    driver_path = "./chromedriver"
    options.add_argument('user-agent='+user_agent)

    driver = webdriver.Chrome(executable_path=driver_path, chrome_options=options)

    return driver

## find rows contain body
def extract_topics(soup):
    topics = {}
    parentPage = 'https://www.udemy.com'
    tables = soup.findAll('div', attrs = {'class':'row'}) 
    
    for row in tables:
        columns = row.findAll('div', attrs = {'class':'column-3'})
        for col in columns:
            uls = col.findAll('ul')
            if (len(uls) != 0):
                for link in uls:
                    for attrib in link.find_all('a', href=True):
                        topics[attrib.text] = parentPage + attrib['href']

    return topics

def pull_html(url, user_agent):
#     ugent = shadow_useragent.ShadowUserAgent()
#     user_agent = ugent.percent(0.05)
    driver = build_driver(user_agent)
    driver.get(url)
    element = WebDriverWait(driver,6).until(
        EC.presence_of_element_located((By.XPATH, "//div[@class='course-price-text price-text--base-price__discount--1J7vF price-text--black--1qJbH price-text--medium--2clK9 price-text--bold--ldWad']"))
    )
    category = WebDriverWait(driver,6).until(
        EC.presence_of_element_located((By.XPATH, "//a[@class='btn btn-quaternary btn-xs']"))
    )
    html = driver.page_source
    test_soup = bs.BeautifulSoup(html, 'lxml')
    test_search = test_soup.find('div', attrs = {'class': re.compile('curriculum-course-card--container*')})
    if test_search is None:
        print "BLOCKED ON " + url
        driver.quit()
        ugent = shadow_useragent.ShadowUserAgent()
        user_agent = ugent.percent(0.05)
        pull_html(url,user_agent)
    driver.quit()
    return driver, html

def find_max_page(html):
    attribute = bs.BeautifulSoup(html, 'lxml')
    
    ul = attribute.find('ul', attrs = {'class':'pagination pagination-expanded'})
    max_page = 1
    if ul is not None:
        for page in ul.find_all('li'):
            if len(page.text) > 0:
                next_page = int(page.text)
                if max_page < next_page:
                    max_page = next_page
    return max_page

def first_layer_course_info(topic, html):  
    sub_frame = pd.DataFrame(columns=['Course','URL','instructor',
                           'Price (full)','Price (discount)','Rank'])
    
    sub_req = bs.BeautifulSoup(html, 'lxml')
    
    courses = sub_req.find_all('div', attrs = {'class': re.compile('curriculum-course-card--container*')})
    category_elem = sub_req.find('div', attrs = {'class': re.compile('browse-container suppress-xl*')})
    category = category_elem.find('a', attrs = {'class': re.compile('btn btn-quaternary btn-xs')}, href=True)
    for course in courses:
        title = course.find('div', attrs = {'class': re.compile('list-view-course-card--title*')})
        instructor = course.find('div', attrs = {'class': re.compile('list-view-course-card--instructor*')})
        rate_price = course.find('div', attrs = {'class': re.compile('list-view-course-card--price-rating*')})
        course_url = course.find('a', href=True)
        
        if title is None:
            continue
        
        prices = re.compile("(\d+.\d{2}|Free)")
        ratings = re.compile("\d.\d\(.*\)")
        
        string_no_rate = re.sub('\d.\d\(.*\)', '', rate_price.text)
        course_price = prices.findall(string_no_rate)
        
        o_price = '0'
        c_price = '0'
        rank = ''

        if(len(course_price) == 2):
            o_price = course_price[1]
            c_price = course_price[0]
        elif (len(course_price) == 1):
            o_price = '0'
            c_price = course_price[0]
            
        if ratings is not None:
            rank = ratings.search(rate_price.text).group()
        else:
            rank = ''
        
        data = Orderd{'Course':title.text,
                 'URL':'www.udemy.com'+course_url['href'],
                 'instructor':instructor.text,
                 'Price (full)':o_price,
                 'Price (discount)':c_price,
                 'Rank':rank,
                 'Category 1': category.text,
                 'Category 2': '',
                 'Category 3': topic}
        
        sub_frame = sub_frame.append(pd.DataFrame([data],index=[0]), ignore_index=True, sort=False)
    return sub_frame

def scrape(topic, url, user_agent):
    print "Starting : " + topic
    df = pd.DataFrame(columns=['Course','URL','instructor',
                           'Price (full)','Price (discount)','Rank','Category 1','Category 2','Category 3'])
    driver,html = pull_html(url,user_agent)
    driver.quit()
    page_count = find_max_page(html)
    frame = first_layer_course_info(topic, html)
    df = df.append(frame, ignore_index=True, sort=False)
    for i in range(2, page_count+1):
        next_url = url+"?p="+str(i)
        print next_url
        driver, html = pull_html(next_url, user_agent)
        frame = first_layer_course_info(topic, html)
        df = df.append(frame, ignore_index=True, sort=False)
        
    return driver,df

# agent = ua.percent(0.05)
agent = ua.random
headers = {'User-Agent': agent}
req_url = 'https://www.udemy.com/sitemap'
req = Request(url=req_url, headers=headers) 
html = urlopen(req).read()

soup = bs.BeautifulSoup(html,'html5lib')
topics = extract_topics(soup)

# lock = threading.Lock()

def task(topic, job_list):
    ugent = shadow_useragent.ShadowUserAgent()
    user_agent = ugent.percent(0.05)
    url = topics[topic]
    drv,dframe = scrape(topic, url, user_agent)
    dframe.to_csv('./out/'+topic+'.csv', index = None, header=True,encoding = 'utf-8')

done = [os.path.split(s)[1].rsplit('.', 1)[0] for s in glob.glob(os.getcwd() + "/out/*.csv")]
counter = 0
for topic in topics:
    if topic not in done:
        if counter == 10:
            break
        counter += 1
        t1 = threading.Thread(target=task, args=(topic,done, ))
        t1.start()

