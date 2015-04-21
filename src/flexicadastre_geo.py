# coding: utf-8
import os
import json
import glob
# import dataset
# from normality import slugify
# from datetime import datetime
from pprint import pprint # noqa

from common import DATA_PATH
from layers import LAYERS

SOURCE_PATH = os.path.join(DATA_PATH, 'flexicadastre', 'raw')
try:
    os.makedirs(SOURCE_PATH)
except:
    pass

DEST_PATH = os.path.join(DATA_PATH, 'flexicadastre', 'geo')
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

    if ctx['source_name'] not in ['MZ']:
        return

    out = {
        "type": "FeatureCollection",
        "features": []
    }

    for layer in ctx.get('layers'):
        if layer['name'] not in LAYERS or not LAYERS[layer['name']]:
            continue

        for fdata in layer.pop('data').get('features'):
            # print feature.get('geometry').get('rings')
            attrs = get_attrs(fdata)
            if not attrs.get('parties') or \
                    not fdata.get('geometry', {}).get('rings'):
                continue

            # print fdata.get('geometry')

            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': fdata.get('geometry', {}).get('rings')
                },
                'properties': {
                    'layer': layer.get('name'),
                    'parties': attrs.get('parties')
                }
            }
            out['features'].append(feature)
        # pprint(layer)

    out_path = os.path.basename(path)
    with open(os.path.join(DEST_PATH, out_path), 'wb') as fh:
        json.dump(out, fh)


if __name__ == '__main__':
    for file_path in glob.glob(os.path.join(SOURCE_PATH, '*')):
        parse_file(file_path)
