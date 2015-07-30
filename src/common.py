import os
import logging
import dataset

DATABASE_URI = os.environ.get('DATABASE_URI')
assert DATABASE_URI is not None

DATA_PATH = os.environ.get('DATA_PATH')
assert DATA_PATH is not None

database = dataset.connect(DATABASE_URI)

import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

logging.basicConfig(level=logging.INFO)
logging.getLogger('requests').setLevel(logging.WARNING)
