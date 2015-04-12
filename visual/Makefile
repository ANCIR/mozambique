
all: clean build

build: maps/moz.json maps/moz_c.json js/deps.js data/persons.csv

clean:
	rm -f maps/moz.json
	rm -f maps/moz_c.json
	rm -f js/deps.js
	rm -rf js/vendor

maps/admin1.zip:
	mkdir -p maps
	wget -O maps/admin1.zip http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_1_states_provinces.zip
	unzip -n -d maps maps/admin1.zip

maps/places.zip:
	mkdir -p maps
	wget -O maps/places.zip http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_populated_places.zip
	unzip -n -d maps maps/places.zip

maps/moz.json: maps/admin1.zip maps/places.zip
	rm -f maps/subunits.json
	ogr2ogr \
		-f GeoJSON \
		-where "ADM0_A3 IN ('MOZ')" \
		maps/subunits.json \
		maps/ne_10m_admin_1_states_provinces.shp

	rm -f maps/places.json
	ogr2ogr \
		-f GeoJSON \
		-where "SCALERANK < 5 AND ADM0_A3 IN ('MOZ')" \
		maps/places.json \
		maps/ne_10m_populated_places.shp

	topojson -o maps/moz.json \
		-- \
		maps/subunits.json \
		maps/places.json

maps/moz_c.json: maps/admin1.zip maps/places.zip
	topojson -o maps/concessions.json \
		--properties layer=layer,parties=parties \
		-- \
		concessions=../data/flexicadastre/geo/MZ.json

	topojson -o maps/moz_c.json \
		--id-property adm1_code \
		--properties name=NAME,layer=layer,parties=parties \
		--bbox \
		-- \
		maps/concessions.json \
		maps/subunits.json \
		maps/places.json

data/persons.csv:
	mkdir -p data
	cp ../data/exports/concession_persons.csv data/persons.csv

js/deps.js:
	bower install
	uglifyjs --screw-ie8 -c -o js/deps.js \
		js/vendor/underscore/underscore.js \
		js/vendor/speakingurl/speakingurl.min.js \
		js/vendor/d3/d3.js \
		js/vendor/topojson/topojson.js

