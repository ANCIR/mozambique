
var companies = {},
    persons = {},
    filterState = {
      'pinned': null
    };

var mapboxEl = d3.select("#map-container"),
    loadingEl = d3.select("#loading"),
    width = parseFloat(mapboxEl.style('width').replace('px', '')) * 0.9,
    height = width * 1.5,
    svg = d3.select("#map").append("svg")
      .attr("width", width)
      .attr("height", height);

var concessionsSel = null,
    personsSel = null,
    companiesSel = null;


d3.json('maps/moz_c.json', function(error, mapData) {
  d3.csv('data/persons.csv', function(error, linkage) {
    processLinkageData(linkage, mapData);
    renderMap(mapData);
    renderLists();
    toggleLoading(false);
  });
});


var nsSlug = function(cls, name) {
  return cls + '-' + getSlug(name);
};


var toggleLoading = function(state) {
  loadingEl.classed('hidden', !state);
};


var processLinkageData = function(linkage, mapData) {
  var concessions = {};
  companies = {};
  persons = {};

  for (var j in mapData.objects.concessions.geometries) {
    var feat = mapData.objects.concessions.geometries[j];
    var slug = feat.properties.slug = nsSlug('a', feat.properties.parties);
    if (_.isUndefined(concessions[slug])) {
      concessions[slug] = 0;
    }
    concessions[slug] += 1;
  }

  for (var i in linkage) {
    var row = linkage[i];
    var companySlug = nsSlug('c', row.company_name);
    var personSlug = nsSlug('p', row.company_person_name);
    var partiesSlug = nsSlug('a', row.conc_parties);

    if (_.isUndefined(companies[companySlug])) {
      companies[companySlug] = {
        'name': row.company_name,
        'slug': companySlug,
        'id': row.company_id,
        'date': row.company_date,
        'concessions': concessions[partiesSlug],
        'parties': partiesSlug, 
        'persons': []
      };
    }
    if (companies[companySlug]['persons'].indexOf(personSlug) == -1) {
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
    if (persons[personSlug]['companies'].indexOf(companySlug) == -1) {
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
      .attr("d", path);

  svg.selectAll(".concession")
      .data(concessions.features)
    .enter().append("path")
      .attr("class", "concession")
      .attr("d", path);

  concessionsSel = svg.selectAll(".concession-shape")
      .data(concessions.features)
    .enter().append("path")
      .attr("class", "concession-shape")
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

  personsSel = d3.select("#persons").selectAll('li')
      .data(personsList)
    .enter()
      .append("li")
      .text(function(d) { return d.name + ' (' + d.concessions + ')'; })
      .on('mouseenter', function(d) {
        hoverEntity(d.slug, 'relevant');
      })
      .on('mouseleave', function(d) {
        hoverEntity(null, 'relevant');
      })
      .on('click', function(d) {
        var o = filterState.pinned == d.slug ? null : d.slug;
        filterState.pinned = o;
        hoverEntity(o, 'hidden', true);
        hoverEntity(o, 'pinned', false);
      });

  var companiesList = _.sortBy(_.values(companies), function(c) {
    return c.concessions * -1;
  });

  companiesSel = d3.select("#companies").selectAll('li')
      .data(companiesList)
    .enter()
      .append("li")
      .text(function(d) { return d.name + ' (' + d.concessions + ')'; })
      .on('mouseenter', function(d) {
        hoverEntity(d.slug, 'relevant');
      })
      .on('mouseleave', function(d) {
        hoverEntity(null, 'relevant');
      })
      .on('click', function(d) {
        var o = filterState.pinned == d.slug ? null : d.slug;
        filterState.pinned = o;
        hoverEntity(o, 'hidden', true);
        hoverEntity(o, 'pinned', false);
      });
};

var relatedItems = function(slug) {
  if (!slug) return [];
  var related = [slug];
  if(_.has(companies, slug)) {
    related = related.concat(companies[slug].persons);
  }
  if(_.has(persons, slug)) {
    related = related.concat(persons[slug].companies);
  }
  for (var i in related) {
    var x = related[i];
    if (_.has(companies, x)) {
      related.push(companies[x].parties);
    }
  }
  return related;
};

var hoverEntity = function(target, cls, inverted) {
  inverted = inverted ? true : false;
  if (!target) {
    companiesSel.classed(cls, false);
    personsSel.classed(cls, false);
    concessionsSel.classed(cls, false);
  } else {
    var relevant = relatedItems(target);
    //console.log(relevant, filterState.hover);
    companiesSel.classed(cls, function(d) {
      return inverted ^ relevant.indexOf(d.slug) != -1;
    });
    personsSel.classed(cls, function(d) {
      return inverted ^ relevant.indexOf(d.slug) != -1;
    });
    concessionsSel.classed(cls, function(d) {
      return inverted ^ relevant.indexOf(d.properties.slug) != -1;
    });
  }
};

