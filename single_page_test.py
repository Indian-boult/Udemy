#!/usr/bin/env python

import bs4 as bs
from urllib2 import urlopen, Request
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import re
from fake_useragent import UserAgent
import time 
import shadow_useragent
import copy

ugent = shadow_useragent.ShadowUserAgent()
user_agent = ugent.percent(0.05)

url = 'https://www.udemy.com/topic/youtube-marketing/?p=14'

PROXY = "45.32.231.36:31280"

options = webdriver.ChromeOptions()
options.add_argument("--incognito")
options.binary_location = '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser'
driver_path = "./chromedriver"
options.add_argument('user-agent='+user_agent)
options.add_argument('--proxy-server=%s' % PROXY)
# options.add_argument('--user-data-dir=/Users/thai/Library/Application Support/Google/Chrome/Default')
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Chrome(executable_path=driver_path,chrome_options=options)
driver.get(url)
element = WebDriverWait(driver,5).until(
#     "//div[@class='list-view-course-card--price-rating--3vt-J']"
    EC.presence_of_element_located((By.XPATH, "//div[@class='course-price-text price-text--base-price__discount--1J7vF price-text--black--1qJbH price-text--medium--2clK9 price-text--bold--ldWad']")))
# time.sleep(4)
html = driver.page_source
test_soup = bs.BeautifulSoup(html, 'lxml')


courses = test_soup.find_all('div', attrs = {'class': re.compile('curriculum-course-card--container*')})
category = WebDriverWait(driver,5).until(
    EC.presence_of_element_located((By.XPATH, "//a[@class='btn btn-quaternary btn-xs']")))
for course in courses:
    title = course.find('div', attrs = {'class': re.compile('list-view-course-card--title*')})
    instructor = course.find('div', attrs = {'class': re.compile('list-view-course-card--instructor*')})
    rate_price = course.find('div', attrs = {'class': re.compile('list-view-course-card--price-rating*')})
    
    if title is None:
        continue
    
    course_url = course.find('a', href=True)
    
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
            
    print category.text
    print title.text
    print instructor.text
    print course_price
    print o_price
    print c_price



