import os
import re
import hashlib
import unicodecsv
import dataset
try:
    import cPickle as pickle
except ImportError:
    import pickle
from Levenshtein import distance
from normality import normalize
from common import database, DATA_PATH

flexi_table = database['mz_flexicadastre']
hermes_company = database['hermes_company']
hermes_relation = database['hermes_relation']
pep_table = database['pep']
company_aliases = database['company_aliases']
person_aliases = database['person_aliases']

REPLS = {
    r's\.a\.r\.l\.?': 'sarl',
    r's\.a\.?': 'sa',
    r'[, ]+(lda|ltd).?': ' limitada',
    r'\( ?(moz|mozambique|moc).?\)': '',
    r'\([0-9,\.]*%?\)': ''
}

REPLS = {re.compile(k): v for k, v in REPLS.items()}


def make_slug(sec, key):
    key = hashlib.sha1(key.encode('utf-8')).hexdigest()
    return '%s%s' % (sec, key[:8])


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
    names = {}
    for row in table:
        name = row.get(name_field)
        if name is None or len(name) <= 2:
            continue
        if name not in names:
            names[name] = {
                'name': name,
                'count': 0,
                'fp': fingerprint(name)
            }
        names[name]['count'] += 1

    names = names.values()
    with open(pp, 'wb') as fh:
        pickle.dump(names, fh)
    return names

HOLDERS = get_names(flexi_table, 'parties')
print '* Loaded %s concession contract partners' % len(HOLDERS)

COMPANIES = get_names(hermes_company, 'nome_da_entidade')
print '* Loaded %s registered companies' % len(COMPANIES)

PEPS = get_names(pep_table, 'full_name')
print '* Loaded %s politically exposed persons' % len(PEPS)


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


def generate_aliases(table, ref_list, match_list, dist_limit=3):
    comps = 0.0
    total_comps = float(max(1, len(ref_list) * len(match_list)))
    for ref in ref_list:
        if not table.find_one(name=ref['name']):
            table.insert({
                'name': ref['name'],
                'fp': ref['fp'],
                'canonical': ref['name']
            })

        for match in match_list:
            dist = distance(match['fp'], ref['fp'])
            comps += 1.0
            if comps and comps % 100000 == 0:
                pct_comps = int((comps / total_comps) * 100)
                print '%s matching: %s%%' % (table.table.name, pct_comps)
            if dist < dist_limit:
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

# read_aliases(company_aliases)
# generate_aliases(company_aliases, HOLDERS, COMPANIES)


def load_aliases(table):
    aliases = {}
    for row in table:
        aliases[row['canonical']] = row['canonical']
        aliases[row['name']] = row['canonical']
    return aliases

all_c_aliases = load_aliases(company_aliases)
COMPANIES = {}
for holder in HOLDERS:
    canon = all_c_aliases[holder['name']]

    slug = make_slug('c', canon)
    if slug not in COMPANIES:
        COMPANIES[slug] = {
            'name': canon,
            # 'slug': slug,
            'parties': [],
            'persons': [],
            'concessions': 0
        }

    if holder['name'] not in COMPANIES[slug]['parties']:
        COMPANIES[slug]['parties'].append(holder['name'])
        COMPANIES[slug]['concessions'] += holder['count']


print '* Identified %s concession-holding entities by %s names' % \
    (len(COMPANIES), len(all_c_aliases))

PERSONS = []
for person in hermes_relation.find(rel_key='socios_pessoas'):
    comp = person.get('source_name')
    if comp not in all_c_aliases:
        continue

    name = person.get('target_name')
    PERSONS.append({
        'name': name,
        'comp': all_c_aliases[comp],
        'fp': fingerprint(name)
    })

print '* Identified %s company-related person names' % len(PERSONS)
# read_aliases(person_aliases)
# generate_aliases(person_aliases, PERSONS + PEPS, [])

all_p_aliases = load_aliases(person_aliases)
UPERSONS = {}
for person in PERSONS:
    cslug = make_slug('c', person['comp'])
    if cslug not in COMPANIES:
        continue

    canon = all_p_aliases[person['name']]
    slug = make_slug('p', canon)
    if slug not in UPERSONS:
        UPERSONS[slug] = {
            'name': canon,
            # 'slug': slug,
            'companies': [],
            'concessions': 0
        }

    if cslug not in UPERSONS[slug]['companies']:
        UPERSONS[slug]['companies'].append(cslug)
        comp = COMPANIES[cslug]
        UPERSONS[slug]['concessions'] += comp['concessions']
        if slug not in comp['persons']:
            comp['persons'].append(slug)

print '* Identified %s unique persons' % len(UPERSONS)

import json
with open('tmp.json', 'wb') as fh:
    json.dump({'persons': UPERSONS, 'companies': COMPANIES}, fh)

