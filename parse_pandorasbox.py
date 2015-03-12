# coding: utf-8
import os
import re
import json
from lxml import html
from normality import slugify
import dataset

MES = {
    "01": "Janeiro",
    "02": "Fevereiro",
    "03": u"Março",
    "04": "Abril",
    "05": "Maio",
    "06": "Junho",
    "07": "Julho",
    "08": "Agosto",
    "09": "Setembro",
    "10": "Outubro",
    "11": "Novembro",
    "12": "Dezembro"
}

engine = dataset.connect('sqlite:///pandora.sqlite3')
companies = engine['company']
relations = engine['relation']


def parse(path, data):
    doc = html.fromstring(data.get('body'))
    data = {'file_path': path}
    rels = []
    for row in doc.findall('.//table//table//tr'):
        label, value = row.findall('.//td')
        label = label.text_content()
        key = slugify(label, sep='_')
        # value = value.text_content()
        for script in value.findall('script'):
            if 'MesExtenso' in script.text:
                script.text = script.text.replace('MesExtenso("', '')
                script.text = script.text.replace('")', '')
                script.text = MES.get(script.text)
            if 'Relaciona' in script.text:
                # print [script.text]
                match = re.match(r'Relaciona\((.*)\)$', script.text)
                lst = json.loads('[%s]' % match.group(1))
                name = lst[1].strip()
                assert lst[1] == lst[2], lst
                script.text = None
                rels.append({
                    'rel_label': label,
                    'rel_key': key,
                    'target_name': name
                })
            # value.remove(script)
        value = value.text_content()
        if len(value.strip()) and len(key):
            data[key] = value.strip()

    print 'Parsing %r' % data.get('nome_da_entidade')
    companies.upsert(data, ['id_do_registo'])
    for rel in rels:
        rel['id_do_registo'] = data.get('id_do_registo')
        rel['source_name'] = data.get('nome_da_entidade')
        relations.upsert(rel, ['id_do_registo', 'rel_label', 'target_name'])


def notices():
    for dirname, _, filenames in os.walk('data'):
        for filename in filenames:
            path = os.path.join(dirname, filename)
            with open(path, 'rb') as fh:
                try:
                    data = json.load(fh)
                except ValueError:
                    os.unlink(path)
                parse(path, data)

if __name__ == '__main__':
    notices()
    dataset.freeze(companies, format='csv', filename='pan_companies.csv')
    dataset.freeze(relations, format='csv', filename='pan_relations.csv')

