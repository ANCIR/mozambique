
all: flexi hermes boletin

clean:
	rm -rf env
	rm -rf flexicadastre/raw/*

env/bin/python:
	virtualenv env
	env/bin/pip install -r requirements.txt

flexiscrape: env/bin/python
	env/bin/python src/flexicadastre_scrape.py

flexiparse: env/bin/python
	env/bin/python src/flexicadastre_parse.py

flexi: flexiscrape flexiparse

boletin:
	env/bin/python src/boletin_scrape.py

hermesscrape: env/bin/python
	env/bin/python src/hermes_scrape.py

hermesparse: env/bin/python
	env/bin/python src/hermes_parse.py

hermes: hermesscrape hermesparse
