# coding: utf-8
import os
import json
import glob
# import dataset
from normality import slugify
# from datetime import datetime
from pprint import pprint # noqa

from common import DATA_PATH

SOURCE_PATH = os.path.join(DATA_PATH, 'flexicadastre', 'raw')
try:
    os.makedirs(SOURCE_PATH)
except:
    pass

DEST_PATH = os.path.join(DATA_PATH, 'flexicadastre', 'geo_layers')
try:
    os.makedirs(DEST_PATH)
except:
    pass


def get_attrs(feature):
    out = {}
    for k, v in feature.get('attributes').items():
        k = k.lower().strip()
        out[k] = v
    return out


def parse_file(path):
    with open(path, 'rb') as fh:
        ctx = json.load(fh)

    if ctx['source_name'] not in ['TZ']:
        return

    for layer in ctx.get('layers'):
        out = {
            "type": "FeatureCollection",
            "features": []
        }

        for fdata in layer.pop('data').get('features'):
            attrs = get_attrs(fdata)
            if not fdata.get('geometry', {}).get('rings'):
                continue

            props = dict(attrs)
            props['layer'] = layer.get('name')
            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': fdata.get('geometry', {}).get('rings')
                },
                'properties': props
            }
            out['features'].append(feature)

        name = slugify('%s %s' % (ctx['source_name'], layer.get('name')),
                       sep='_')
        name = name + '.json'
        with open(os.path.join(DEST_PATH, name), 'wb') as fh:
            json.dump(out, fh)


if __name__ == '__main__':
    for file_path in glob.glob(os.path.join(SOURCE_PATH, '*')):
        parse_file(file_path)
