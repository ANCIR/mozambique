PY=env/bin/python
PIP=env/bin/python
IN2CSV=env/bin/in2csv

all: flexi hermes boletin pep

install: env/bin/python

clean:
	rm -rf env
	rm -rf flexicadastre/raw/*
	rm data/pep/cip3.csv

env/bin/python:
	virtualenv env
	$(PIP) install -r requirements.txt

flexiscrape: env/bin/python
	$(PY) src/flexicadastre_scrape.py

flexiparse: env/bin/python
	$(PY) src/flexicadastre_parse.py

flexi: flexiscrape flexiparse

boletin:
	$(PY) src/boletin_scrape.py

hermesscrape: env/bin/python
	$(PY) src/hermes_scrape.py

hermesparse: env/bin/python
	$(PY) src/hermes_parse.py

hermes: hermesscrape hermesparse

data/pep/cip3.csv:
	$(IN2CSV) --format xls -u 2 data/pep/cip3.xlsm >data/pep/cip3.csv

pep: env/bin/python data/pep/cip3.csv
	$(PY) src/pep_parse.py
