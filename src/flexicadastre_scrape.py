from itertools import count
import logging
import requests
import json
import os
import re

from common import DATA_PATH

log = logging.getLogger('flexiscrape')

SITES = {
    'BW': 'http://portals.flexicadastre.com/botswana/',
    'UG': 'http://portals.flexicadastre.com/uganda/',
    'NA': 'http://portals.flexicadastre.com/Namibia/',
    'MZ': 'http://portals.flexicadastre.com/mozambique/en/',
    'KE': 'http://map.miningcadastre.go.ke/map',
    'RW': 'http://portals.flexicadastre.com/rwanda/',
    'TZ': 'http://portal.mem.go.tz/map/',
    'ZM': 'http://portals.flexicadastre.com/zambia/',
    'CD': 'http://portals.flexicadastre.com/drc/en/',
    'SS': 'http://portals.flexicadastre.com/southsudan/'
}

QUERY = {
    'where': '1=1',
    'outFields': '*',
    'geometryType': 'esriGeometryPolygon',
    'spatialRel': 'esriSpatialRelIntersects',
    #'units': 'esriSRUnit_Meter',
    'outSR': 102100,  # wgs 84
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


def scrape_layers(sess, data, token, rest_url):
    res = sess.get(rest_url, params={'f': 'json', 'token': token})
    print 'Scraping %s at %s' % (data['source_title'], rest_url)
    for layer in res.json().get('layers'):
        layer['rest_url'] = rest_url
        query_url = '%s/%s/query' % (rest_url, layer['id'])
        q = QUERY.copy()
        q['token'] = token
        layer['query_url'] = query_url
        print ' -> Layer: [%(id)s] %(name)s ' % layer
        for i in count(0):
            q['resultOffset'] = q['resultRecordCount'] * i
            res = sess.get(query_url, params=q)
            page = res.json()
            # print page
            if 'data' not in layer:
                layer['data'] = page
            else:
                layer['data']['features'].extend(page['features'])
            if not page.get('exceededTransferLimit'):
                break
        data['layers'].append(layer)

    # print 'Entries:', len(data['layers'])
    return data


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
        cfg = json.loads(json.loads(text))

        token = cfg['Extras'].pop()

        data = {
            'source_name': name,
            'source_title': cfg['Title'],
            'source_url': url,
            # 'rest_url': rest_url,
            'layers': []
        }

        try:
            for service in cfg['MapServices']:
                if service['MapServiceType'] == 'Features':
                    rest_url = service['RestUrl']
                    data = scrape_layers(sess, data, token, rest_url)

            path = os.path.join(STORE_PATH, '%s.json' % name)
            with open(path, 'wb') as fh:
                json.dump(data, fh)
        except Exception, e:
            log.exception(e)


if __name__ == '__main__':
    scrape_configs()
