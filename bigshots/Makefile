
all: clean build

build: maps/moz.json maps/moz_c.json assets

clean:
	rm -f maps/moz.json
	rm -f maps/moz_c.json
	rm -f assets/deps.js
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

.PHONY: maps/moz_c.json
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

assets/deps.js:
	bower install
	uglifyjs --screw-ie8 -c -o assets/deps.js \
		vendor/underscore/underscore.js \
		vendor/speakingurl/speakingurl.min.js \
		vendor/d3/d3.js \
		vendor/topojson/topojson.js

.PHONY: assets
assets: assets/deps.js
	lessc -x style/style.less assets/style.css

watch:
	watchr -e "watch('.*') { system 'make assets' }"
