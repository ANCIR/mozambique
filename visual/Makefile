
all: maps/moz.json

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
		--id-property adm1_code \
		--properties name=NAME \
		--bbox \
		-- \
		maps/subunits.json \
		maps/places.json

clean:
	rm maps/moz.json
	# rm -rf maps
