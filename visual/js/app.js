
var companies = {},
    persons = {};

var bbox = d3.select("#map-container"),
    width = parseFloat(bbox.style('width').replace('px', '')) * 0.9,
    height = width * 1.5,
    svg = d3.select("#map").append("svg")
      .attr("width", width)
      .attr("height", height);


d3.json('maps/moz_c.json', function(error, mapData) {
  d3.csv('data/persons.csv', function(error, linkage) {
    processLinkageData(linkage, mapData);
    renderMap(mapData);
    renderLists();
  });
});


var processLinkageData = function(linkage, mapData) {
  var concessions = {};
  companies = {};
  persons = {};

  for (var j in mapData.objects.concessions.geometries) {
    var feat = mapData.objects.concessions.geometries[j];
    var slug = feat.properties.slug = getSlug(feat.properties.parties);
    if (_.isUndefined(concessions[slug])) {
      concessions[slug] = 0;
    }
    concessions[slug] += 1;
  }

  for (var i in linkage) {
    var row = linkage[i];
    var companySlug = getSlug(row.company_name);
    var personSlug = getSlug(row.company_person_name);
    var partiesSlug = getSlug(row.conc_parties);

    if (_.isUndefined(companies[companySlug])) {
      companies[companySlug] = {
        'name': row.company_name,
        'slug': companySlug,
        'id': row.company_id,
        'date': row.company_date,
        'concessions': concessions[partiesSlug],
        'persons': []
      };
    }
    if (_.indexOf(companies[companySlug]['persons'], personSlug) == -1) {
      companies[companySlug]['persons'].push(personSlug);
      companies[companySlug]['degree'] = companies[companySlug]['persons'].length;
    }
    
    if (_.isUndefined(persons[personSlug])) {
      persons[personSlug] = {
        'name': row.company_person_name,
        'slug': personSlug,
        'companies': [],
        'concessions': 0,
        //'roles': [] // TOOD PEP roles
      };  
    }
    if (_.indexOf(persons[personSlug]['companies'], companySlug) == -1) {
      persons[personSlug]['companies'].push(companySlug);
      persons[personSlug]['concessions'] += concessions[partiesSlug];
      persons[personSlug]['degree'] = persons[personSlug]['companies'].length;
    }
  }
};


var renderMap = function(data) {
  var subunits = topojson.feature(data, data.objects.subunits);
  var places = topojson.feature(data, data.objects.places);
  var concessions = topojson.feature(data, data.objects.concessions);

  var projection = d3.geo.orthographic()
    .scale(width * 5)
    .translate([width / 2, height / 2.5])
    .center(d3.geo.centroid(subunits));

  var path = d3.geo.path()
    .projection(projection);

  svg.selectAll(".region")
      .data(subunits.features)
    .enter().append("path")
      .attr("class", function(d) {
        var clazz = "region " + d.id;
        return clazz;
      })
      .attr("d", path)
      .on("click", function(d) {
        
      })
      .on("mouseenter", function(d) {
        var self = d3.select(this);
        d.baseClass = self.attr('class');
        self.attr('class', d.baseClass + ' hovered');
      })
      .on("mouseleave", function(d) {
        var self = d3.select(this);
        self.attr('class', d.baseClass);  
      });

  svg.selectAll(".concession")
      .data(concessions.features)
    .enter().append("path")
      .attr("class", "concession")
      .attr("d", path);

  svg.append("path")
    .datum(places)
    .attr("d", path)
    .attr("class", "place");

  svg.selectAll(".place-label")
      .data(places.features)
    .enter().append("text")
      .attr("class", "place-label")
      .attr("transform", function(d) {
        return "translate(" + projection(d.geometry.coordinates) + ")"; }
      )
      .attr("dy", ".35em")
      .attr("x", function(d) {
        return d.geometry.coordinates[0] > -1 ? 6 : -6; }
      )
      .style("text-anchor", function(d) {
        return d.geometry.coordinates[0] > -1 ? "start" : "end"; }
      )
      .text(function(d) {
        return d.properties.name; }
      );
};


var renderLists = function() {
  var personsList = _.sortBy(_.values(persons), function(p) {
    return p.concessions * -1;
  });

  d3.select("#persons").selectAll('li')
      .data(personsList)
    .enter()
      .append("li")
      .text(function(d) { return d.name + ' (' + d.concessions + ')'; });

  var companiesList = _.sortBy(_.values(companies), function(c) {
    return c.concessions * -1;
  });

  d3.select("#companies").selectAll('li')
      .data(companiesList)
    .enter()
      .append("li")
      .text(function(d) { return d.name + ' (' + d.concessions + ')'; });

}
