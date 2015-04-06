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

## Exploring the data

The following is a guided tour / documentation of the data. Queries are shown as raw SQL, but can be largely ignored in favour of the linked result sets by those not familiar with the language.

### Linking concessions and company data

We'll start exploring the data from the concessions. The table ``mz_flexicadastre`` combines all layers from the source data, which we can summarize like this: 

```sql
SELECT layer_name, COUNT(*) FROM mz_flexicadastre
    GROUP BY layer_name
    ORDER BY COUNT(*) DESC;
```
**[result](http://databin.pudo.org/t/d1be77)**

Next, we can have a look at the most interesting field in this table, ``parties`` - the set of all company and person names which hold mineral rights. Let's see who is top of the list.

```sql
SELECT NORMTXT(parties), COUNT(*) FROM mz_flexicadastre
    WHERE parties IS NOT NULL
    GROUP BY NORMTXT(parties)
    ORDER BY COUNT(*) DESC;
```
**[result](http://databin.pudo.org/t/c859c4)** (NOTE: ``NORMTXT`` is a custom SQL function, defined in ``src/setup.sql``)

We can run the same sort of query on the scraped data from the company register. We would expect that there is only a single entry for each entity name, but that is not true:

```sql
SELECT NORMTXT(nome_da_entidade), COUNT(*) FROM hermes_company
    WHERE nome_da_entidade IS NOT NULL
    GROUP BY NORMTXT(nome_da_entidade)
    ORDER BY COUNT(*) DESC;
```
**[result](http://databin.pudo.org/t/d08f83)**

It seems that a single entity name in the company register will often occur multiple times. An explanation could be that Hermes' data entry failed to reconcile multiple notices regarding a single company in the gazette. Concerned about the data quality of the Hermes Pandora dataset.

Next, let's try and join between both datasets, i.e. see how many of the concession holder entries match company records. To do this, we'll generate normalized versions of the company names on both the company registry and the concessions data.

```sql
SELECT fx.parties_norm, COUNT(fx.id)
    FROM hermes_company AS co, mz_flexicadastre AS fx
    WHERE
        co.nome_da_entidade_norm IS NOT NULL
        AND fx.parties_norm IS NOT NULL
        AND co.nome_da_entidade_norm = fx.parties_norm
    GROUP BY fx.parties_norm
    ORDER BY COUNT(fx.id) DESC;
```
**[result](http://databin.pudo.org/t/d1f3b6)**

This is much better than assumed, the expectation was to find barely any overlap. Out of 2430 distinct company names in the concessions data, 160 are an immediate match. We can also loosen the join criterion using PostgreSQL's ``LEVENSHTEIN`` function which returns the edit distance between two strings:

```sql
SELECT fx.parties_norm, COUNT(fx.id)
    FROM hermes_company AS co, mz_flexicadastre AS fx
    WHERE
        co.nome_da_entidade_norm IS NOT NULL
        AND fx.parties_norm IS NOT NULL
        AND LEVENSHTEIN(co.nome_da_entidade_norm, fx.parties_norm) < 3
    GROUP BY fx.parties_norm
    ORDER BY COUNT(fx.id) DESC;
```

Unfortunately, this query takes pretty much forever. An alternative approach might be to generate a lookup table with ``LEVENSHTEIN`` distances.

### Linking PEPs and company data

To link politically exposed persons (PEP) data with the Hermes company registry, we need to first explore the ``hermes_relation`` table, which contains information on all relations indicated in the Hermes database. It shows us that the relations table has several types of data:

```sql
SELECT DISTINCT rel_label, rel_key FROM hermes_relation;
```
 rel_label             | rel_key                  | Meaning
 --------------------- | ------------------------ | -------------
 Sócios instituições : | ``socios_instituicoes``  | related institutions
 Sócios pessoas :      | ``socios_pessoas``       | related people
 Lugar da sede :       | ``lugar_da_sede``        | headquarters
 

 

## Glossary

* ``MIREM`` - Mozambique, Ministry of Mineral Resources (MIREM)
* See also: [Google Translate PT -> EN](https://translate.google.com/#pt/en/todas%20licencas%20extinto)

## Credit

The project is lead by Don Hubert with [Resources for Development Consulting](http://www.res4dev.com/) in collaboration with [CIP](http://www.cip.org.mz/). Technical support is provided by [ANCIR](http://investigativecenters.org/) in collaboration with [ICFJ](http://icfj.org/).
