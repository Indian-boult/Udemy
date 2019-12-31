#!/usr/bin/env python

'''
level 3 scrape
'''

get_ipython().system('/Users/thai/anaconda2/lib/python2.7/site-packages/shadow_useragent/getpk.sh')

import time 
import shadow_useragent
import copy, sys, os, re, random
import glob
import threading
import bs4 as bs
import pandas as pd
import requests
from datetime import date
import queue
from fake_useragent import UserAgent
from urllib2 import urlopen, Request
from urllib2 import HTTPError
import warnings
warnings.filterwarnings("ignore")

sys.setrecursionlimit(10**6)

PROXIE_LIST = ['http://144.202.65.136:1441', 'http://144.202.65.136:1440',
               'http://144.202.65.136:1441', 'http://144.202.65.136:1442',
               'http://144.202.65.136:1443','http://144.202.65.136:1444']
new_cols = ['Category 1', 'Category 2', 'Category 3', 'Enrollment', 'Language', 'Description', 'Last Update', 'Date Scraped']

def scrape_html(html, date_scraped):
    soup = bs.BeautifulSoup(html, 'lxml')
    
    private = soup.find('div', attrs = {'class':'col-sm-4 col-sm-push-4 col-xs-8 col-xs-push-2'})
    private_2 = soup.find('i', attrs = {'class': 'udi udi-warning'})
    
    if (private is not None) or (private_2 is not None):
        print "private"
        none = ["None"] * len(new_cols)
        return dict(zip(new_cols,none))
    
    enrollment = soup.find('div', attrs = {'data-purpose' : 'enrollment'})
    last_update = soup.find('div', attrs = {'class': 'last-update-date'})
    language = soup.find('div', attrs = {'class': 'clp-lead__locale'})
    description = soup.find('div', attrs = {'class' : 'clp-lead__headline'})
    categories = [cat.text.strip("\n") for cat in soup.find_all('a', attrs = {'class': 'topic-menu__link'})]
    
    try:
        cat = [" ", " ", " "]
        for idx in range(len(categories)):
            cat[idx] = categories[idx]
        
        data = [cat[0], cat[1], cat[2], enrollment.text.strip(" \n").split(" ")[0], 
                language.text.strip("\n"), description.text.strip("\n"),
                last_update.text.strip("\n").split(" ")[-1], date_scraped]
        
        data_dict = dict(zip(new_cols,data))
        
        return data_dict
    except Exception:
        raise Exception()

def scrape_single_url(url, proxies, user_agent, date_scraped):
    ua = shadow_useragent.ShadowUserAgent()
    agent = ua.percent(0.05)
    headers = {'user-agent': user_agent}
        
    proxies = { 'http' : random.choice(PROXIE_LIST) }
    
    try:
        ua = shadow_useragent.ShadowUserAgent()
        agent = ua.percent(0.05)
        headers = {'user-agent': user_agent}
        
        proxies = { 'http' : random.                                                                    (PROXIE_LIST) }
        
        req = requests.get(url=url, proxies=proxies, headers=headers, timeout=6)
        req.encoding = 'ISO-8859-1'
        html = req.text
        if (req.url != url):
            print "Course Removed"
            none = ["None"] * len(new_cols)
            return dict(zip(new_cols,none))
        
        if (req.status_code == 200): 
            data = scrape_html(html, date_scraped)
            return data
        elif req.status_code == 403:
            print req.status_code
            time.sleep(1800)
            return scrape_single_url(url, proxies, agent, date_scraped)
        else:
            print req.status_code
            time.sleep(3)
            return scrape_single_url(url, proxies, agent, date_scraped)
    except Exception as e:
        print e
        time.sleep(2)
        return scrape_single_url(url, proxies, agent, date_scraped)

def pull_info(csv_in, proxies, user_agent, date_scraped):
    out_file = os.path.basename(csv_in)
    df = pd.read_csv(csv_in)
    if 'Category 1' in df:
        df = df.drop(['Category 1','Category 2', 'Category 3'], axis=1)

    urls = list(df['URL'])
    
    new_frame = pd.DataFrame(columns=new_cols)
        
    for idx in range(len(df.index)):
        url = 'https://' + urls[idx]
        print str(idx) + "/" + str(len(df)) + ": " + url
        time.sleep(2)
        if (idx+1 % 300 == 0):
            time.sleep(90)
        data = scrape_single_url(url, proxies, user_agent, date_scraped)
        new_frame = new_frame.append(data, ignore_index=True)
    df = pd.concat([df, new_frame], axis=1)
    df.to_csv('./final/'+out_file, index = None, header=True,encoding = 'utf-8')
    
    print csv_in + " :DONE"

    return df

def task(csv, proxies):
    ua = shadow_useragent.ShadowUserAgent()
    agent = ua.percent(0.05)
    today = date.today()
    date_string = today.strftime("%m/%d/%y")
    df = pull_info(csv, proxies, agent, date_string)

done = [os.path.split(s)[1] for s in glob.glob(os.getcwd() + "/final/*.csv")]
all_files = glob.glob('./out'+ "/*.csv")
todos = [os.path.split(f)[1] for f in all_files if os.path.split(f)[1] not in done]

def worker():
    while True:
        item = q.get()
        if item is None:
            break
        proxies = {'http': random.choice(PROXIE_LIST)}
        task(item,proxies)
        time.sleep(30)

q = queue.Queue()
for item in todos:
    q.put('./out/' + item)
q.put(None)

worker()

'''
THREADS = 3

threads = []
for i in range(THREADS):
     time.sleep(1)
     t = threading.Thread(target=worker)
     t.start()
     threads.append(t)

for t in threads:
     t.join()
'''
