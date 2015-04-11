
var width = 450,
  height = 600,
  svg = d3.select("#map").append("svg")
    .attr("width", width)
    .attr("height", height);

d3.json('maps/moz.json', function(error, data) {
  var subunits = topojson.feature(data, data.objects.subunits);
  var places = topojson.feature(data, data.objects.places);

  // console.log(data);
  // console.log(d3.geo.centroid(subunits));

  var projection = d3.geo.orthographic()
    .scale(2100)
    .translate([width / 2.5, height / 2.5])
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

  svg.append("path")
    .datum(places)
    .attr("d", path)
    .attr("class", "place");

  svg.selectAll(".place-label")
      .data(places.features)
    .enter().append("text")
      .attr("class", "place-label")
      .attr("transform", function(d) { return "translate(" + projection(d.geometry.coordinates) + ")"; })
      .attr("dy", ".35em")
      .attr("x", function(d) { return d.geometry.coordinates[0] > -1 ? 6 : -6; })
      .style("text-anchor", function(d) { return d.geometry.coordinates[0] > -1 ? "start" : "end"; })
      .text(function(d) { return d.properties.name; });    

});
