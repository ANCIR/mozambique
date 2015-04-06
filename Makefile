PY=env/bin/python
PIP=env/bin/python
IN2CSV=env/bin/in2csv
PSQL=psql $(DATABASE_URI) -f

all: flexi hermes boletin pep

install: env/bin/python setup

sqlsetup:
	$(PSQL) src/setup.sql

clean:
	rm -rf env
	rm -rf flexicadastre/raw/*
	rm data/pep/cip3.csv

env/bin/python:
	virtualenv env
	$(PIP) install -r requirements.txt

flexiscrape: env/bin/python
	$(PY) src/flexicadastre_scrape.py

flexiparse: env/bin/python sqlsetup
	$(PY) src/flexicadastre_parse.py
	$(PSQL) src/flexicadastre_cleanup.sql

flexidrop:
	$(PSQL) src/flexicadastre_drop.sql

flexi: flexiscrape flexiparse

boletin:
	$(PY) src/boletin_scrape.py

hermesscrape: env/bin/python
	$(PY) src/hermes_scrape.py

hermesparse: env/bin/python sqlsetup
	$(PY) src/hermes_parse.py
	$(PSQL) src/hermes_cleanup.sql

hermes: hermesscrape hermesparse

data/pep/cip3.csv:
	$(IN2CSV) --format xls -u 2 data/pep/cip3.xlsm >data/pep/cip3.csv

pep: env/bin/python data/pep/cip3.csv
	$(PY) src/pep_parse.py

cleanup: sqlsetup
	$(PSQL) src/flexicadastre_cleanup.sql
	$(PSQL) src/hermes_cleanup.sql
	$(PSQL) src/pep_cleanup.sql
