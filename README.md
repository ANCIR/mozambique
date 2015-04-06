# Mozambique Extractives / PEP Project

This project aims to perform data anlysis on an integrated dataset of company information, extractives concessions data and a set of politically exposed persons (PEPs). The goal is to find conflicts of interest and linkages between PEPs and mining/drilling rights. 

## Data Sources

The data is partially extracted from public sources, from semi-public data sources and from manually conducted research by [CIP](http://www.cip.org.mz/).

### FlexiCadastre

The ``flexicadastre_scrape.py`` and ``flexicadastre_parse.py`` scripts are importers for [FlexiCadastre](http://www.spatialdimension.com/Map-Portals), a GIS solution developed by SpatialDimension and used to store extractives licensing info for a variety of countries. 

### Hermes Pandoras Box

[Hermes](http://hermes.panbox.co.mz/) is an effort to extract structured data from bulletins released as Part III of the official gazette of Mozambique. The data holds information on companies registered in the country since the late seventies, as well as associated personalities. It is unclear if a) the data is complete and verified, and b) this dataset if considered an official release by the Government of Mozambique.

### Politically Exposed Persons

This dataset is manually curated by researchers at [CIP](http://www.cip.org.mz/). It lists key personel in top positions of government and [FRELIMO](https://en.wikipedia.org/wiki/FRELIMO). The tabular layout is inspired by the [Popolo](http://www.popoloproject.com/) data standard.

### Boletin

The scraper for the [public section of the Mozambican government gazette](http://www.portaldogoverno.gov.mz/Legisla/boletinRep/) will download all published PDF files that form Part III. Documents will also be uploaded to [sourceAFRICA](https://sourceafrica.net/) automatically, if the necessary credentials are provided. 

## Setup and configuration

All ETL scripts in this package are geared towards generating tables in a SQL database. Many of them will only work when used against PostgreSQL 9.3 or later (i.e. with support for the ``LEVENSHTEIN()`` function). Your database should be created with the UTF-8 encoding, e.g. with the command:

```bash
$ createdb -E utf-8 mozambique
```

Before running any of the scripts, make sure to set the environment variables explained in ``env.tmpl.sh``, specifically ``DATABASE_URI`` which must be a valid connection string of the form ``postgresql://user:password@host/database_name``. If you wish to upload updated versions of the government gazette to sourceAFRICA, you also need to specify your credentials as ``DOCCLOUD_USER`` and ``DOCCLOUD_PASS``.

Finally, you must ensure that Python's [virtualenv](https://virtualenv.pypa.io/en/latest/) package is installed and available on the system path.

All ETL commands in this package are specified through the ``Makefile`` which can be studied for the available targets. To install all Python dependencies, for example, run the following command:

```bash
$ make install
```

If you want to execute a specific set of scrapers and data loaders, you can call up specific targets:

```bash
$ make flexi
$ make hermes
$ make pep
$ make boletin
```

This should leave you with a freshly stocked SQL database for your analytical pleasure.

## Credit

The project is lead by Don Hubert with [Resources for Development Consulting](http://www.res4dev.com/) in collaboration with [CIP](http://www.cip.org.mz/). Technical support is provided by [ANCIR](http://investigativecenters.org/) in collaboration with [ICFJ](http://icfj.org/).
