from itertools import count
import requests
import json
import os
import re

from common import DATA_PATH

SITES = {
    'NA': 'http://portals.flexicadastre.com/Namibia/',
    'MZ': 'http://portals.flexicadastre.com/mozambique/en/',
    'KE': 'http://map.miningcadastre.go.ke/map',
    'RW': 'http://portals.flexicadastre.com/rwanda/',
    'TZ': 'http://portal.mem.go.tz/map/',
    'CD': 'http://portals.flexicadastre.com/drc/en/'
}

QUERY = {
    'where': '1=1',
    'outFields': '*',
    'geometryType': 'esriGeometryPolygon',
    'spatialRel': 'esriSpatialRelIntersects',
    'units': 'esriSRUnit_Meter',
    'resultRecordCount': 500,
    'resultOffset': 0,
    'returnGeometry': 'true',
    'f': 'pjson'
}

STORE_PATH = os.path.join(DATA_PATH, 'flexicadastre', 'raw')
try:
    os.makedirs(STORE_PATH)
except:
    pass


def scrape_layers(sess, name, title, url, token, rest_url):
    res = sess.get(rest_url, params={'f': 'json', 'token': token})
    data = {
        'source_name': name,
        'source_title': title,
        'source_url': url,
        'rest_url': rest_url,
        'layers': []
    }
    print 'Scraping %(source_title)s at %(source_url)s' % data
    for layer in res.json().get('layers'):
        query_url = '%s/%s/query' % (rest_url, layer['id'])
        q = QUERY.copy()
        q['token'] = token
        layer['query_url'] = query_url
        print ' -> Layer: [%(id)s] %(name)s ' % layer
        for i in count(0):
            q['resultOffset'] = q['resultRecordCount'] * i
            res = sess.get(query_url, params=q)
            page = res.json()
            if 'data' not in layer:
                layer['data'] = page
            else:
                layer['data']['features'].extend(page['features'])
            if not page.get('exceededTransferLimit'):
                break
        data['layers'].append(layer)

    # print 'Entries:', len(data['layers'])

    path = os.path.join(STORE_PATH, '%s.json' % name)
    with open(path, 'wb') as fh:
        json.dump(data, fh)


def scrape_configs():
    for name, url in SITES.items():
        sess = requests.Session()
        res = sess.get(url)
        groups = re.search(r"MainPage\.Init\('(.*)'", res.content)
        text = groups.group(1)
        text = text.replace("\\\\\\'", "")
        text = text.replace("\\'", "")
        text = text.replace('\\\\\\"', "")

        text = '"%s"' % text
        data = json.loads(json.loads(text))

        token = data['Extras'].pop()
        title = data['Title']
        for service in data['MapServices']:
            if service['MapServiceType'] == 'Features':
                rest_url = service['RestUrl']
                scrape_layers(sess, name, title, url, token, rest_url)


if __name__ == '__main__':
    scrape_configs()
