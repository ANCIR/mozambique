# coding: utf-8
import os
import requests
from normality import slugify
from urllib import urlretrieve
from urlparse import urljoin
from lxml import html

from common import DATA_PATH

AUTH = (os.environ.get('DOCCLOUD_USER'),
        os.environ.get('DOCCLOUD_PASS'))
HOST = os.environ.get('DOCCLOUD_HOST', 'https://sourceafrica.net')
PROJECT_ID = os.environ.get('DOCCLOUD_PROJECTID', '230')


def documentcloudify(file_name, data):
    title = data.get('file').replace('.pdf', '')
    title = '%s - %s' % (data['issue'], title)
    search_url = urljoin(HOST, '/api/search.json')
    params = {'q': 'projectid:"%s" title:"%s"' % (PROJECT_ID, title)}
    res = requests.get(search_url, params=params, auth=AUTH,
                       verify=False)
    found = res.json()
    if found.get('total') > 0:
        return found.get('documents')[0].get('canonical_url')
    req_data = {
        'title': title,
        'source': u'Boletins da República',
        'published_url': data.get('url'),
        'access': 'public',
        'language': 'por',
        'project': PROJECT_ID
    }
    files = {
        'file': open(file_name, 'rb')
    }
    upload_url = urljoin(HOST, '/api/upload.json')
    res = requests.post(upload_url, files=files,
                        verify=False, auth=AUTH, data=req_data)
    return res.json().get('canonical_url')


def content_links(url):
    res = requests.get(url)
    doc = html.fromstring(res.text)
    for a in doc.findall('.//div[@id="content"]//a'):
        urlref = urljoin(url, a.get('href', ''))
        if urlref == url:
            continue
        if not urlref.startswith(url):
            continue
        yield urlref, a


def get_files(data):
    url = data.get('issue_url')
    for href, a in content_links(url):
        d = data.copy()
        d['file'] = a.text_content()
        if href.endswith('/view'):
            href, _ = href.rsplit('/view', 1)
        if not href.endswith('.pdf'):
            continue
        d['url'] = href
        file_name = slugify(d['file'], sep='_')
        path = slugify(d['issue'], sep='_')
        file_name = os.path.join(DATA_PATH, 'boletin', path, file_name)
        try:
            os.makedirs(os.path.dirname(file_name))
        except:
            pass
        print [file_name]
        if not os.path.isfile(file_name):
            urlretrieve(d['url'], file_name)
        documentcloudify(file_name, d)


def get_issues(data):
    url = data.get('year_url')
    for href, a in content_links(url):
        d = data.copy()
        d['issue'] = a.text_content()
        d['issue_url'] = href
        get_files(d)


def get_years():
    url = 'http://www.portaldogoverno.gov.mz/Legisla/boletinRep/'
    for href, a in content_links(url):
        # print [a.text_content()]
        data = {
            'year': a.text_content(),
            'year_url': a.get('href')
        }
        get_issues(data)


get_years()
