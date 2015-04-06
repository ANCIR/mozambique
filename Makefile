PY=env/bin/python
PIP=env/bin/python
IN2CSV=env/bin/in2csv
PSQL=psql $(DATABASE_URI)
FREEZE=datafreeze --db $(DATABASE_URI)

CORPXT=tar xvfz data/corpwatch/csv.tar.gz -C data/corpwatch --strip-components=1
CORPCSV=env/bin/csvsql -t -S --db $(DATABASE_URI) --insert


all: flexi hermes boletin pep

install: env/bin/python setup

sqlsetup:
	$(PSQL) src/setup.sql

clean:
	rm -rf env
	rm -rf flexicadastre/raw/*
	rm -f data/pep/cip3.csv
	rm -f data/corpwatch/csv.tar.gz
	rm -f data/corpwatch/companies.csv
	rm -f data/corpwatch/company_relations.csv
	rm -f data/corpwatch/company_locations.csv

env/bin/python:
	virtualenv env
	$(PIP) install -r requirements.txt

flexiscrape: env/bin/python
	$(PY) src/flexicadastre_scrape.py

flexiparse: env/bin/python sqlsetup
	$(PY) src/flexicadastre_parse.py
	$(PSQL) -f src/flexicadastre_cleanup.sql

flexidrop:
	$(PSQL) -f src/flexicadastre_drop.sql

flexi: flexiscrape flexiparse

boletin:
	$(PY) src/boletin_scrape.py

hermesscrape: env/bin/python
	$(PY) src/hermes_scrape.py

hermesparse: env/bin/python sqlsetup
	$(PY) src/hermes_parse.py
	$(PSQL) -f src/hermes_cleanup.sql

hermes: hermesscrape hermesparse

data/corpwatch/csv.tar.gz:
	mkdir -p data/corpwatch 
	curl -o data/corpwatch/csv.tar.gz http://api.corpwatch.org/documentation/db_dump/corpwatch_api_tables_csv.tar.gz

data/corpwatch/companies.csv: data/corpwatch/csv.tar.gz
	$(CORPXT) corpwatch_api_tables_csv/companies.csv
	$(PSQL) -c "DROP TABLE IF EXISTS corpwatch_companies"
	$(CORPCSV) --tables corpwatch_companies data/corpwatch/companies.csv

data/corpwatch/company_relations.csv: data/corpwatch/csv.tar.gz
	$(CORPXT) corpwatch_api_tables_csv/company_relations.csv
	$(PSQL) -c "DROP TABLE IF EXISTS corpwatch_company_relations"
	$(CORPCSV) --tables corpwatch_company_relations data/corpwatch/company_relations.csv

data/corpwatch/company_locations.csv: data/corpwatch/csv.tar.gz
	$(CORPXT) corpwatch_api_tables_csv/company_locations.csv
	$(PSQL) -c "DROP TABLE IF EXISTS corpwatch_company_locations"
	$(CORPCSV) --tables corpwatch_company_locations data/corpwatch/company_locations.csv

corpwatch: data/corpwatch/companies.csv data/corpwatch/company_relations.csv data/corpwatch/company_locations.csv

data/pep/cip3.csv:
	$(IN2CSV) --format xls -u 2 data/pep/cip3.xlsm >data/pep/cip3.csv

pep: env/bin/python data/pep/cip3.csv
	$(PY) src/pep_parse.py

pep-companies:
	$(FREEZE) src/pep_companies.yaml

pep-concessions:
	$(FREEZE) src/pep_concessions.yaml

clean-data: sqlsetup
	$(PSQL) -f src/flexicadastre_cleanup.sql
	$(PSQL) -f src/hermes_cleanup.sql
	$(PSQL) -f src/pep_cleanup.sql
	$(PSQL) -f src/finalize.sql

reports: clean-data pep-companies pep-concessions
