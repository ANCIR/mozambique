# coding: utf-8
import os
import json
import glob
import unicodecsv
from normality import slugify
from datetime import datetime
from pprint import pprint # noqa

from common import DATA_PATH, database

SOURCE_PATH = os.path.join(DATA_PATH, 'pep')
try:
    os.makedirs(SOURCE_PATH)
except:
    pass


def row_empty(row):
    value = ''.join(row.values())
    return len(value.strip()) < 0


def convert_row(row):
    out = {}
    for field, value in row.items():
        field = slugify(field, sep='_')
        value = value.strip()
        # TODO handle excel dates etc.
        if not len(value):
            continue
        out[field] = value
    return out


def get_name(row):
    name = '%s %s %s' % (row.get('given_name', ''),
                         row.get('additional_name', ''),
                         row.get('family_name', ''))
    name = name.replace('  ', ' ')
    return name


def parse_file(path):
    tbl = database['pep']
    tbl.delete()
    with open(path, 'rb') as fh:
        for row in unicodecsv.DictReader(fh):
            if row_empty(row):
                continue
            row = convert_row(row)
            row['full_name'] = get_name(row)
            # pprint(row)
            tbl.insert(row)


if __name__ == '__main__':
    for file_path in glob.glob(os.path.join(SOURCE_PATH, '*.csv')):
        parse_file(file_path)
