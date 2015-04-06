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
SELECT f_normtxt(parties), COUNT(*) FROM mz_flexicadastre
    WHERE parties IS NOT NULL
    GROUP BY f_normtxt(parties)
    ORDER BY COUNT(*) DESC;
```
**[result](http://databin.pudo.org/t/c859c4)** (NOTE: ``f_normtxt`` is a custom SQL function, defined in ``src/setup.sql``)

We can run the same sort of query on the scraped data from the company register. We would expect that there is only a single entry for each entity name, but that is not true:

```sql
SELECT f_normtxt(nome_da_entidade), COUNT(*) FROM hermes_company
    WHERE nome_da_entidade IS NOT NULL
    GROUP BY f_normtxt(nome_da_entidade)
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
 
Next, we can try and make a connection between the PEP table and the 'associated people'.

```sql
SELECT hr.target_name_norm, COUNT(*)
    FROM hermes_relation AS hr, pep AS pe
    WHERE
        hr.target_name_norm IS NOT NULL
        AND LENGTH(hr.target_name_norm) > 2
        AND hr.rel_key = 'socios_pessoas'
        AND pe.full_name_norm IS NOT NULL
        AND hr.target_name_norm = pe.full_name_norm
    GROUP BY hr.target_name_norm
    ORDER BY COUNT(*) DESC;
```
**[results](http://databin.pudo.org/t/13d779)**

This is the first result in our data expedition which has some journalistic value. In total, it shows 40 matching names. It seems like Central Committee member Marina Pachinuapa and Governor Paulo Auade are good businesspeople, with a dozen companies in their name, each.

A very important caveat is that this is based purely on name matching, so it would be necessary to validate (e.g. via the Boletin) that these people actually are the same.

Again, we can make that search fuzzy based on ``LEVENSHTEIN`` distance, which expands the result set from 40 to a total of 111 potential matches.

```sql
SELECT hr.target_name_norm, COUNT(*)
    FROM hermes_relation AS hr, pep AS pe
    WHERE
        hr.target_name_norm IS NOT NULL
        AND LENGTH(hr.target_name_norm) > 2
        AND hr.rel_key = 'socios_pessoas'
        AND pe.full_name_norm IS NOT NULL
        AND LEVENSHTEIN(hr.target_name_norm, pe.full_name_norm) < 3
    GROUP BY hr.target_name_norm
    ORDER BY COUNT(*) DESC;
```
**[results](http://databin.pudo.org/t/ded591)**

Based on this linkage, we can generate a full report of possible matches for further inquiry. We'll use ``datafreeze`` to export a CSV file for this query:

```sql
SELECT hc.id_do_registo AS company_id,
		hc.nome_da_entidade AS company_name,
       hr.target_name AS company_person_name,
       pe.given_name AS pep_given_name,
       pe.family_name AS pep_family_name,
       pe.menbership_role AS pep_menbership_role,
       pe.organization_name AS pep_organization_name
    FROM hermes_company AS hc, hermes_relation AS hr, pep AS pe
    WHERE hc.id_do_registo = hr.id_do_registo
       AND hr.target_name_norm IS NOT NULL
       AND LENGTH(hr.target_name_norm) > 2
       AND hr.rel_key = 'socios_pessoas'
       AND pe.full_name_norm IS NOT NULL
       AND LEVENSHTEIN(hr.target_name_norm, pe.full_name_norm) < 3;
```

The full CSV output is available at [reports/pep_companies.csv](reports/pep_companies.csv).

### Making the full link: PEP to Concessions

Given our preliminary experiments in joining concessions to companies, and companies to PEPs, we can how look for any direct associations. I'll eat my bicycle if we get any matches.

```sql
      SELECT fx.layer_name AS conc_layer_name,
             fx.name AS conc_name,
             fx.parties AS conc_parties,
             hc.id_do_registo AS company_id,
             hc.nome_da_entidade AS company_name,
             hr.target_name AS company_person_name,
             pe.given_name AS pep_given_name,
             pe.family_name AS pep_family_name,
             pe.menbership_role AS pep_menbership_role,
             pe.organization_name AS pep_organization_name
          FROM hermes_company AS hc, hermes_relation AS hr,
               pep AS pe, mz_flexicadastre AS fx
          WHERE hc.id_do_registo = hr.id_do_registo
             AND fx.parties_norm = hc.nome_da_entidade_norm
             AND hr.target_name_norm IS NOT NULL
             AND LENGTH(hr.target_name_norm) > 2
             AND hr.rel_key = 'socios_pessoas'
             AND pe.full_name_norm IS NOT NULL
             AND LEVENSHTEIN(hr.target_name_norm, pe.full_name_norm) < 3;
```

There's a few candidates. The full CSV output is available at [reports/pep_concessions.csv](reports/pep_concessions.csv).

To expand the set of matches to be less precise, we're re-writing the normalization functions to account for common variations in the way that company and people names are written: 

```sql
CREATE OR REPLACE FUNCTION f_mz_company(t varchar) RETURNS varchar AS $$
  BEGIN
    RETURN TRIM(
      regexp_replace(
        regexp_replace(
          regexp_replace(
            regexp_replace(
              regexp_replace(
                f_normtxt(t),
                '\([0-9,\.]*%?\)', '', 'g'
              ),
              '\( ?(moz|mozambique|moc).?\)', '', 'g'
            ),
            '[, ]+(lda|ltd)\.?', ' limitada', 'g'
          ),
          '\W+', ' ', 'g'
        ),
        '\s+', ' ', 'g'
      )
    );
  END;
$$ LANGUAGE plpgsql;
```

While this is monstrous, all it really does is: remove all percentages in brackets (e.g. ``(100.0%)`` on concessions), remove references to Mozambique in brackets, replace mentions of ``lda`` with ``limitada``, replace all non-text characters with whitespace, and finally, collapse all consecutive whitespace.

This increases the number of potential concession matches from 5 to 33, the number of PEP-held companies from 111 to 250.

### Learning more about the company data

Taking a step back, the company registry dataset is probably the most interesting one, because it provides a rich source of different linkages. Let's start by having a look at the companies with the most people associated with them:

```sql
SELECT hc.id_do_registo,
        LEFT(MAX(hc.nome_da_entidade), 80) AS company_name,
        MIN(data_da_escritura),
        COUNT(DISTINCT hr.target_name_norm)
    FROM hermes_company AS hc, hermes_relation AS hr
    WHERE hc.nome_da_entidade IS NOT NULL
        AND hc.id_do_registo = hr.id_do_registo
        AND hr.rel_key = 'socios_pessoas'
    GROUP BY hc.id_do_registo, hc.nome_da_entidade_norm
    ORDER BY COUNT(DISTINCT hr.target_name_norm) DESC;
```
**[results](http://databin.pudo.org/t/a180e3)**

A lot of the top-ranking companies seem to be trade associations and unions, which makes sense. Obviously, the reverse question is much more interesting: who are the people associated with the largest number of companies?

```sql
SELECT MAX(hr.target_name) AS name,
        COUNT(DISTINCT hc.nome_da_entidade_norm) AS companies
    FROM hermes_company AS hc, hermes_relation AS hr
    WHERE LENGTH(hr.target_name_norm) > 1
        AND hc.id_do_registo = hr.id_do_registo
        AND hr.rel_key = 'socios_pessoas'
    GROUP BY hr.target_name_norm
    ORDER BY COUNT(DISTINCT hc.nome_da_entidade_norm) DESC;
```
**[results](http://databin.pudo.org/t/6886db)**

The top guy, José Manuel Caldeira, appears to be a corporate lawyer and probably acts as a secretary for the 106 companies he is tied to, but most of the other names on this list don't show up much on Google. I'm relatively sure that in the hands of an experienced Mozambican journalist, this list would yield some interesting leads.

Given that we now have improved normalization of company and person names, it also makes sense to return to the mining concessions. First, let's look at the companies with the most concessions there again: 

```sql
SELECT parties_norm, COUNT(*) FROM mz_flexicadastre
    WHERE parties_norm IS NOT NULL
    GROUP BY parties_norm
    ORDER BY COUNT(*) DESC;
```
**[results](http://databin.pudo.org/t/86779c)**

Interestingly, not to many big international names show up here, although the top ten do include two companies that appear to be from China - not a surprise, we're talking about African resources.

We can also link all the way across to the associated persons to make a simplified table of the big shots in Mozambican mining:

```sql
SELECT MAX(hr.target_name) AS name,
        COUNT(DISTINCT hc.nome_da_entidade_norm) AS companies,
        COUNT(DISTINCT fx.id) AS concessions
    FROM hermes_company AS hc,
        hermes_relation AS hr,
        mz_flexicadastre AS fx
    WHERE fx.parties_norm = hc.nome_da_entidade_norm
        AND LENGTH(hr.target_name_norm) > 1
        AND hc.id_do_registo = hr.id_do_registo
        AND hr.rel_key = 'socios_pessoas'
    GROUP BY hr.target_name_norm
    ORDER BY COUNT(DISTINCT fx.id) DESC;
```
**[results](http://databin.pudo.org/t/ebc8f9)**

The result from this query is very informative in two ways: it tells us that we have a lot of work left with regards to data de-duplication, but it also shows that just looking at companies connected to concessions is not enough: there's clearly a lot of connectivity between different concession holders, they share large parts of their boards.

## Glossary

* ``MIREM`` - Mozambique, Ministry of Mineral Resources (MIREM)
* See also: [Google Translate PT -> EN](https://translate.google.com/#pt/en/todas%20licencas%20extinto)

## Credit

The project is lead by Don Hubert with [Resources for Development Consulting](http://www.res4dev.com/) in collaboration with [CIP](http://www.cip.org.mz/). Technical support is provided by [ANCIR](http://investigativecenters.org/) in collaboration with [ICFJ](http://icfj.org/).
