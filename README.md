# Mozambique Extractives / PEP Project

This project aims to perform data anlysis on an integrated dataset of company information, extractives concessions data and a set of politically exposed persons (PEPs). The goal is to find conflicts of interest and linkages between PEPs and mining/drilling rights. 

## Data Sources

The data is partially extracted from public sources, from semi-public data sources and from manually conducted research by [CIP](http://www.cip.org.mz/).

### FlexiCadastre ETL

The ``flexicadastre_scrape.py`` and ``flexicadastre_parse.py`` scripts are importers for [FlexiCadastre](http://www.spatialdimension.com/Map-Portals), a GIS solution developed by SpatialDimension and used to store extractives licensing info for a variety of countries. 

### Hermes Pandoras Box

[Hermes](http://hermes.panbox.co.mz/) is an effort to extract structured data from bulletins released as Part III of the official gazette of Mozambique. The data holds information on companies registered in the country since the late seventies, as well as associated personalities. It is unclear if a) the data is complete and verified, and b) this dataset if considered an official release by the Government of Mozambique.

### Politically Exposed Persons

This dataset is manually curated by researchers at [CIP](http://www.cip.org.mz/). It lists key personel in top positions of government and [FRELIMO](https://en.wikipedia.org/wiki/FRELIMO). The tabular layout is inspired by the [Popolo](http://www.popoloproject.com/) data standard.

## Credit

The project is lead by Don Hubert with [Resources for Development Consulting](http://www.res4dev.com/) in collaboration with [CIP](http://www.cip.org.mz/). Technical support is provided by [ANCIR](http://investigativecenters.org/) in collaboration with [ICFJ](http://icfj.org/).
