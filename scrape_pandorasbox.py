import os
import json
import time
import requests

URL = 'http://hermes.panbox.co.mz/index.php'
QUERY_URL = 'http://hermes.panbox.co.mz/pesquisa.php'
LOGIN_URL = 'http://hermes.panbox.co.mz/php/scripts/auth.php'
LOGOUT_URL = 'http://hermes.panbox.co.mz/php/scripts/logout.php'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.115 Safari/537.36' # noqa

QUERY = {
    'tipo': '1',
    'campo1': '990',
    'expressao1': '1',
    'conector1': 'x',
    'campo2': 'x',
    'expressao2': '',
    'conector2': 'x',
    'campo3': 'x',
    'expressao3': '',
    'conector3': 'x',
    'campo4': 'x',
    'expressao4': '',
    'conector4': 'x',
    'campo5': 'x',
    'expressao5': '',
    'formato': '1',
    'contador': '10',
    'Buscar': 'Executar'
}


def make_session():
    sess = requests.Session()
    sess.headers.update({'User-Agent': UA})
    sess.get(URL)
    data = {
        'username': 'canallimitada',
        'password': '1234',
        'entrar': 'Entrar',
        'local_ip': None,
        'proxy_ip': '209.222.5.227',
        'path_dir': None
    }
    res = sess.post(LOGIN_URL, data=data)
    assert res.status_code == 200
    # print res.content
    res = sess.get(URL)
    # print res.content
    return sess


def end_session(sess):
    sess.post(LOGOUT_URL)


def load_by_id(sess, id):
    q = QUERY.copy()
    q['expressao1'] = id
    if id % 100 == 0:
        end_session(sess)
        sess = make_session()
    res = sess.post(QUERY_URL, data=q)

    if '../../index.php?erro=-' in res.content:
        # print [res.content]
        end_session(sess)
        sess = make_session()
        return None

    # print [res.content]
    # return None
    data = {
        'headers': dict(res.headers.items()),
        'body': res.content.decode('iso-8859-1'),
        'status': res.status_code
    }
    return data


def cache_path(id):
    path = os.path.join('data', str(id % 100).zfill(2), '%s.json' % id)
    dir = os.path.dirname(path)
    try:
        os.makedirs(dir)
    except:
        pass
    return path


def scrape():
    try:
        sess = make_session()
        for i in xrange(1, 200000):
            path = cache_path(i)
            if os.path.isfile(path):
                print '[%s] skipping: %s' % (i, path)
                continue
            data = load_by_id(sess, i)
            if data is None:
                print '[%s] failed: sleeping' % i
                time.sleep(120)
            else:
                dlen = len(data['body'])
                print '[%s] saving: %s (%s)' % (i, path, dlen)
                with open(path, 'wb') as fp:
                    json.dump(data, fp)
                time.sleep(1)
    finally:
        end_session(sess)


if __name__ == '__main__':
    scrape()
