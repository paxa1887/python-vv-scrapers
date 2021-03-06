import random
import re
from pprint import pprint

import requests
from bs4 import BeautifulSoup

from src.constants.signs import *
from src.keys.db_mongo import mongo_connection
from src.utils.Mongo import Mongo
from src.utils.headless import *
from src.utils.unicode import delete_accents

# CONNECTION
mongo = Mongo(mongo_connection)

# BASICS
stale_data = []
parser = "lxml"

# STALE DATA BASE
list1 = signs_en
list2 = signs_en.copy()
for sign1 in list1:
    for sign2 in list2:
        stale_data.append({
            'type': 'compatibility',
            'sign1': sign1,
            'sign2': sign2,
            'resume': {
                'en': '',
                'es': ''
            },
            'relationship': {
                'en': '',
                'es': ''
            },
            'percents': {
                'intimate': random.randrange(30, 100),
                'mindset': random.randrange(30, 100),
                'feelings': random.randrange(30, 100),
                'priorities': random.randrange(30, 100),
                'interests': random.randrange(30, 100),
                'sport': random.randrange(30, 100),
            }
        })

# ENGLISH
for data in stale_data:
    sign1 = data['sign1'].lower()
    sign2 = data['sign2'].lower()
    url_base = "https://askastrology.com/zodiac-compatibility/" + sign1 + "-compatibility/" + sign1
    url_with_sign = url_base + '-' + sign2
    page = requests.get(url_with_sign, headers={'User-Agent': random_user_agent()})
    soup = BeautifulSoup(page.content, parser)
    compatibility_ps = soup.select('div.entry-content > p')
    try:
        data['resume']['en'] = compatibility_ps[0].text.lstrip()
        data['relationship']['en'] = compatibility_ps[1].text.lstrip()
    except IndexError:
        pprint(url_with_sign)
        page = requests.get(url_with_sign, headers={'User-Agent': random_user_agent()})
        soup = BeautifulSoup(page.content, parser)
        compatibility_ps = soup.select('div.entry-content > p')
        data['resume']['en'] = compatibility_ps[0].text.lstrip()
        data['relationship']['en'] = compatibility_ps[1].text.lstrip()

# SPANISH
for data in stale_data:
    sign1 = delete_accents(signs_en_to_es[data['sign1']].lower())
    sign2 = delete_accents(signs_en_to_es[data['sign2']].lower())
    url_base = "https://www.euroresidentes.com/horoscopos/compatibilidad/" + sign1 + "/" + sign1
    url_with_sign = url_base + '-' + sign2 + '.htm'
    page = requests.get(url_with_sign, headers={'User-Agent': random_user_agent()})

    if page.ok == 0:
        url_base = "https://www.euroresidentes.com/horoscopos/compatibilidad/" + sign1 + "/" + sign1
        url_with_sign = url_base + '-' + sign2 + '.htm'
        page = requests.get(url_with_sign, headers={'User-Agent': random_user_agent()})

    soup = BeautifulSoup(page.content, parser)
    compatibility_ps = soup.select('article.center-block > p')

    if not compatibility_ps:
        url_base = "https://www.euroresidentes.com/horoscopos/compatibilidad/" + sign2 + "/" + sign2
        url_with_sign = url_base + '-' + sign1 + '.htm'
        page = requests.get(url_with_sign, headers={'User-Agent': random_user_agent()})
        soup = BeautifulSoup(page.content, parser)
        compatibility_ps = soup.select('article.center-block > p')

    try:
        data['resume']['es'] = re.sub(' +', ' ', compatibility_ps[0].text.lstrip())
        data['relationship']['es'] = re.sub(' +', ' ', compatibility_ps[2].text.lstrip())
        if not data['relationship']['es']:
            data['relationship']['es'] = re.sub(' +', ' ', compatibility_ps[1].text.lstrip())
    except IndexError:
        page = requests.get(url_with_sign, headers={'User-Agent': random_user_agent()})
        soup = BeautifulSoup(page.content, parser)
        compatibility_ps = soup.select('article.center-block > p')
        data['resume']['es'] = re.sub(' +', ' ', compatibility_ps[0].text.lstrip())
        data['relationship']['es'] = re.sub(' +', ' ', compatibility_ps[2].text.lstrip())

mongo.db.stale.insert_many(stale_data)

exit(0)

