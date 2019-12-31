#!/usr/bin/env python

import time 
import shadow_useragent
import copy, sys, os, re, random
import glob
import threading
import bs4 as bs
import pandas as pd
import requests
from requests import ReadTimeout, ConnectTimeout, HTTPError, Timeout, ConnectionError
from fake_useragent import UserAgent
from urllib2 import urlopen, Request
from urllib2 import HTTPError
import warnings
warnings.filterwarnings("ignore")

def scrape_html(html):
    soup = bs.BeautifulSoup(html, 'lxml')
    
    private = soup.find('div', attrs = {'class':'col-sm-4 col-sm-push-4 col-xs-8 col-xs-push-2'})
    private_2 = soup.find('i', attrs = {'class': 'udi udi-warning'})
    
    enrollment = soup.find('div', attrs = {'data-purpose' : 'enrollment'})
    last_update = soup.find('div', attrs = {'class': 'last-update-date'})
    language = soup.find('div', attrs = {'class': 'clp-lead__locale'})
    description = soup.find('div', attrs = {'class' : 'clp-lead__headline'})
    categories = [cat.text.strip("\n") for cat in soup.find_all('a', attrs = {'class': 'topic-menu__link'})]
    
    if (private is not None) or (private_2 is not None):
        print "private"
        return ["None"] * 8
    
    try:
        cat = [" ", " ", " "]
        for idx in range(len(categories)):
            cat[idx] = categories[idx]
            
        print cat[0]
        print cat[1]
        print cat[2]
        print enrollment.text.strip(" \n").split(" ")[0]
        print language.text.strip("\n")
        print description.text.strip("\n")
        print last_update.text.strip("\n").split(" ")[-1]
        print
    
        data = [cat[0], cat[1], cat[2], enrollment.text.strip(" \n").split(" ")[0], 
                language.text.strip("\n"), description.text.strip("\n"), last_update.text.strip("\n").split(" ")[-1]]
        return data
    except IndexError:
        raise
        
    return data

proxies = { 'http' : 'http://144.202.65.136:1440',
            'http' : 'http://144.202.65.136:1441',
            'http' : 'http://144.202.65.136:1442',
            'http' : 'http://144.202.65.136:1443',
            'http' : 'http://144.202.65.136:1444'}

ua = shadow_useragent.ShadowUserAgent()
agent = ua.random
headers = {'user-agent': agent}
try:
    req_url = 'http://www.udemy.com/course/the-best-aws-solutions-architect-associate/'
    req_url2 = 'https://www.udemy.com/course/icerik-pazarlama-egitimi/'
#     req_url2 = 'https://www.udemy.com/course/corso-web-marketing/'
#     req_url2 = 'https://www.udemy.com/course/making-wealth-from-real-estate/'
    req = requests.get(url=req_url2, proxies=proxies, headers=headers, timeout=5.0) 
    html = req.content
    print req.status_code
    if (req.url != req_url2):
        print "Does not exist"
    else:
        df_single = scrape_html(html)
except (ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError, ):
    print "Too Long"

