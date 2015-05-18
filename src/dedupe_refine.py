# coding: utf-8
import unicodecsv
import os
from common import DATA_PATH, database

table = database['dedupe_company']


def read_file():
    aliases = {}
    with open(os.path.join(DATA_PATH, 'refine_out.csv'), 'rb') as fh:
        for row in unicodecsv.DictReader(fh):
            aliases[row['parties']] = row['parties_match']
    return aliases


def load_refine_aliases():
    for orig, canon in read_file().items():
        canon_data = table.find_one(name_plain=canon)
        data = {
            'name_plain': orig,
            'name_norm': canon_data.get('name_norm')
        }
        print data
        table.update(data, ['name_plain'])


if __name__ == '__main__':
    load_refine_aliases()
