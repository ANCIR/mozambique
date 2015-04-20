import os
import re
import unicodecsv
import dataset
try:
    import cPickle as pickle
except ImportError:
    print "FOO"
    import pickle

from Levenshtein import distance
from normality import normalize
from common import database, DATA_PATH

flexi_table = database['mz_flexicadastre']
hermes_company = database['hermes_company']
hermes_relation = database['hermes_relation']
pep_table = database['pep']
company_aliases = database['company_aliases']

REPLS = {
    r's\.a\.r\.l\.?': 'sarl',
    r's\.a\.?': 'sa',
    r'[, ]+(lda|ltd).?': ' limitada',
    r'\( ?(moz|mozambique|moc).?\)': '',
    r'\([0-9,\.]*%?\)': ''
}

REPLS = {re.compile(k): v for k, v in REPLS.items()}


def fingerprint(name):
    name = name.lower()
    for p, r in REPLS.items():
        # print p, r, name
        name = p.sub(r, name)
    name = normalize(name)
    tokens = set([n for n in name.split(' ') if len(n)])
    return unicode(' '.join(sorted(tokens)))


def get_names(table, name_field):
    pp = os.path.join(DATA_PATH, '%s_names.pickle' % table.table.name)
    if os.path.exists(pp):
        with open(pp, 'rb') as fh:
            return pickle.load(fh)
    names = []
    seen = set()
    for row in table.distinct(name_field):
        name = row.get(name_field)
        if name is None or len(name) <= 2 or name in seen:
            continue
        seen.add(name)
        names.append({
            'name': name,
            'fp': fingerprint(name)
        })

    with open(pp, 'wb') as fh:
        pickle.dump(names, fh)
    return names

HOLDERS = get_names(flexi_table, 'parties')
print '* Loaded %s concession contract partners' % len(HOLDERS)

COMPANIES = get_names(hermes_company, 'nome_da_entidade')
print '* Loaded %s registered companies' % len(COMPANIES)


def read_aliases(table):
    ap = os.path.join(DATA_PATH, '%s.csv' % table.table.name)
    if not os.path.exists(ap):
        return
    with open(ap, 'rb') as fh:
        for row in unicodecsv.DictReader(fh):
            row.pop('id', None)
            try:
                row['distance'] = int(row['distance'])
            except:
                row['distance'] = None
            table.upsert(row, ['name'])


def write_aliases(table):
    ap = os.path.join(DATA_PATH, '%s.csv' % table.table.name)
    dataset.freeze(table, filename=ap, format='csv')


def generate_aliases(table, ref_list, match_list):
    comps = 0
    for ref in ref_list:
        if not table.find_one(name=ref['name']):
            table.insert({
                'name': ref['name'],
                'fp': ref['fp'],
                'canonical': ref['name']
            })

        for match in match_list:
            dist = distance(match['fp'], ref['fp'])
            comps += 1
            if comps and comps % 100000 == 0:
                print '%s matching: %s comparisons' % (table.table.name, comps)
            if dist < 3:
                if not table.find_one(name=match['name']):
                    table.insert({
                        'name': match['name'],
                        'fp': match['fp'],
                        'candidate': ref['name'],
                        'distance': dist,
                        'canonical': match['name']
                    })
                # print 'Match? %r -> %r' % (ref['name'], match['name'])

    write_aliases(table)

#read_aliases(company_aliases)
generate_aliases(company_aliases, HOLDERS, COMPANIES)
