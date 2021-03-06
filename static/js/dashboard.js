// Load Data from backend
var data = {{ case_data|safe }}
var graph = {{ force_layout|safe }}
var dtgFormat = d3.time.format("%Y-%m-%d");

// Format date.
data.forEach(function(d) {
  d.fechas   = dtgFormat.parse(d.fecha);
});

// Custom reduce functions for list elements.
// http://stackoverflow.com/questions/17524627/is-there-a-way-to-tell-crossfilter-to-treat-elements-of-array-as-separate-record
function reduceAdd(attr) {
  return function(p,v) {
    ++p.count
    p.sum += v[attr];
    return p;
  };
}

function reduceRemove(attr) {
  return function(p,v) {
    --p.count
    p.sum -= v[attr];
    return p;
  };
}

function reduceInitial() {
  return {};
}

function reduceAddArray(attr) {
    return function (p, v) {
      if (v[attr][0] === "") return p;    // skip empty values
      v[attr].forEach (function(val, idx) {
         p[val] = (p[val] || 0) + 1; //increment counts
      });
      return p;
    }
}

function reduceRemoveArray(attr) {
    return function (p, v) {
      if (v[attr][0] === "") return p;    // skip empty values
      v[attr].forEach (function(val, idx) {
         p[val] = (p[val] || 0) - 1; //decrement counts
      });
      return p;
    }
}

// Load crossfilter data.
var ndx = crossfilter(data);

// Setup dimensions.
var dateDim = ndx.dimension(function(d) {return d.fechas;});
var corteDim = ndx.dimension(function(d) {return d.corte;});
var provinciaDim = ndx.dimension(function(d) {return d.provincia;});
var juecesDim = ndx.dimension(function(d) {return d.jueces;});
var mapDim = ndx.dimension(function(d) {return d.provincia;});
var cfDim = ndx.dimension(function(d) {return d.provincia;});
var sobreDim = ndx.dimension(function(d) {return d.sobre;});
var vocesDim = ndx.dimension(function(d) {return d.voces;});
var materiaDim = ndx.dimension(function(d) {return d.materia;});

// Setup groups, using custom reduce functions.
var all = ndx.groupAll();
var dateGroup = dateDim.group()
var corteGroup = corteDim.group().reduceCount(function(d) {return d.corte;});
var provinciaGroup = provinciaDim.group().reduceCount(function(d) {return d.provincia;});
var juecesGroup = juecesDim.groupAll().reduce(reduceAddArray("jueces"), reduceRemoveArray("jueces"), reduceInitial).value();
var mapGroup = mapDim.group();
var cfGroup = cfDim.group();
var sobreGroup = sobreDim.group().reduceCount(function(d) {return d.sobre;});
var vocesGroup = vocesDim.groupAll().reduce(reduceAddArray("voces"), reduceRemoveArray("voces"), reduceInitial).value();
var materiaGroup = materiaDim.groupAll().reduce(reduceAddArray("materia"), reduceRemoveArray("materia"), reduceInitial).value();

// hack to make dc.js charts work
function arrayGroupAll() {
  var newObject = [];
  for (var key in this) {
    if (this.hasOwnProperty(key) && key != "all" && key != "top") {
      newObject.push({
        key: key,
        value: this[key]
      });
    }
  }
  return newObject;
};

function arrayGroupTop(count) {
    var newObject = this.all();
     newObject.sort(function(a, b){return b.value - a.value});
    return newObject.slice(0, count);
};

function arrayFilterHandler(dimension, filters) {
   dimension.filter(null);
    if (filters.length === 0)
        dimension.filter(null);
    else
        dimension.filterFunction(function (d) {
            for (var i=0; i < d.length; i++) {
                if (filters.indexOf(d[i]) >= 0) return true;
            }
            return false;
        });
    return filters;
}

// Get date limits.
var minDate = dateDim.bottom(1)[0].fechas;
var maxDate = dateDim.top(1)[0].fechas;

var mainChart  = dc.barChart("#header-chart");
var totalCount = dc.dataCount(".dc-data-count");

// Get div width adn height.
var mainChart_width = $('#header-chart-div').width(),
    mainChart_height = $('#header-chart').height();
var mapChart_width = $('#pais').width(),
    mapChart_height = $('#pais').height();
var minimapChart_width = $('#capital').width(),
    minimapChart_height = $('#capital').height();

// Plot main (count) bar graph.
mainChart
	.width(mainChart_width).height(mainChart_height)
	.dimension(dateDim)
	.group(dateGroup)
	.x(d3.time.scale().domain([minDate,maxDate]))
    .xUnits(function(){return 100;})
    .xAxis().ticks(7);
mainChart.yAxis().ticks(2)

// Get total number of entries.
totalCount
    .dimension(ndx)
    .group(all);

// Map chart function.
function mapChart() {

    var argMap = dc.geoChoroplethChart('#pais');
    var capMap = dc.geoChoroplethChart('#capital');
    
    // Load the 2 geojson files for Argentina and Capital Federal
    d3.json("/static/js/argentina.json", function(geojson1){
        d3.json("/static/js/cf.geojson", function(geojson2){
    
        // Center projection dynamically based on div size. 
        // http://stackoverflow.com/questions/32884406/geojson-projection-with-d3-js-and-dc-js-for-south-africa-and-provinces
        // create a first guess for the map projection
        var map_center = d3.geo.centroid(geojson1)
        var map_scale  = 150;
        var map_offset = [mapChart_width/1.85, mapChart_height/1.7];
        var map_projection = d3.geo.mercator().scale(map_scale).center(map_center)
            .translate(map_offset);
    
        // create the path
        var map_path = d3.geo.path().projection(map_projection);
    
        // using the path determine the bounds of the current map and use 
        // these to determine better values for the scale and translation
        var map_bounds  = map_path.bounds(geojson1);
        var map_hscale  = map_scale*mapChart_width  / (map_bounds[1][0] - map_bounds[0][0]);
        var map_vscale  = map_scale*mapChart_height / (map_bounds[1][1] - map_bounds[0][1]);
        var map_scale   = (map_hscale < map_vscale) ? map_hscale : map_vscale;
        var map_offset  = [mapChart_width - (map_bounds[0][1] + map_bounds[1][0])/3,
                          mapChart_height - (map_bounds[0][1] + map_bounds[1][1])/1.85];
    
        // new projection
        map_projection = d3.geo.mercator().center(map_center)
          .scale(map_scale).translate(map_offset);
        map_path = map_path.projection(map_projection);
    
        // Plot the geochoropleth map with dc.
        argMap
            .dimension(mapDim)
            .group(mapGroup)
            .width(mapChart_width)
            .height(mapChart_height)
            .colors(d3.scale.quantize()
                   .range(["#ecf2f7", "#dae6f0", "#c7d9e8", "#b5cde1",
                       "#a2c0d9", "#90b4d2", "#7da7ca", "#6a9bc3", "#588ebb",
                       "#4682b4"])
                    )
            .colorDomain([0, 100])
            .colorCalculator(function(d) {return d ? argMap.colors()(d) : '#ccc';})
            .transitionDuration(1000)
            .projection(d3.geo.mercator()
                    .center(map_center)
                    .translate(map_offset)
                    .scale(map_scale * .85)
                    )
            .overlayGeoJson(geojson1.features, 'NAME_1', function(d) {
                return d.properties.NAME_1.toUpperCase();
            })
    
          // http://stackoverflow.com/questions/32884406/geojson-projection-with-d3-js-and-dc-js-for-south-africa-and-provinces
          // create a first guess for the minimap projection
          var minimap_center = d3.geo.centroid(geojson2)
          var minimap_scale  = 150;
          var minimap_offset = [minimapChart_width/2, minimapChart_height/2];
          var minimap_projection = d3.geo.mercator().scale(minimap_scale).center(minimap_center)
              .translate(minimap_offset);
    
          // create the path
          var minimap_path = d3.geo.path().projection(minimap_projection);
    
          // using the path determine the bounds of the current map and use 
          // these to determine better values for the scale and translation
          var minimap_bounds  = minimap_path.bounds(geojson2);
          var minimap_hscale  = minimap_scale*minimapChart_width  / (minimap_bounds[1][0] - minimap_bounds[0][0]);
          var minimap_vscale  = minimap_scale*minimapChart_height / (minimap_bounds[1][1] - minimap_bounds[0][1]);
          var minimap_scale   = (minimap_hscale < minimap_vscale) ? minimap_hscale : minimap_vscale;
          var minimap_offset  = [minimapChart_width - (minimap_bounds[0][0] + minimap_bounds[1][0])/2,
                            minimapChart_height - (minimap_bounds[0][1] + minimap_bounds[1][1])/2];
    
          // new projection
          minimap_projection = d3.geo.mercator().center(minimap_center)
            .scale(minimap_scale).translate(minimap_offset);
          minimap_path = minimap_path.projection(minimap_projection);
    
        // Plot the geochoropleth map with dc.
        capMap
            .dimension(cfDim)
            .group(cfGroup)
            .width(minimapChart_width)
            .height(minimapChart_height)
            .colors(d3.scale.quantize()
                   .range(["#ecf2f7", "#dae6f0", "#c7d9e8", "#b5cde1",
                       "#a2c0d9", "#90b4d2", "#7da7ca", "#6a9bc3", "#588ebb",
                       "#4682b4"])
                    )
            .colorDomain([0, 100])
            .colorCalculator(function(d) {return d ? argMap.colors()(d) : '#ccc';})
            .transitionDuration(1000)
            .projection(d3.geo.mercator()
                    .center(minimap_center)
                    .translate(minimap_offset)
                    .scale(minimap_scale * .85)
                    )
            .overlayGeoJson(geojson2.features, 'NAME_1', function(d) {
                return d.properties.NAME_1.toUpperCase();
            })
        dc.renderAll();
        });
    });
};

// Display data table.
var datatable   = dc.dataTable("#dc-data-table");

datatable
    .dimension(dateDim)
    .group(function(d) {return "";})
    .size(data.length)
    // dynamic columns creation using an array of closures
    .columns([
        function(d) {return d.autos;},
        function(d) {return d.fecha;},
        function(d) {return d.corte;},
        function(d) {return d.jueces;},
        function(d) {return d.sobre;}
    ]).sortBy(function(d) {
        return d.Value;
    })
    .order(d3.descending);
    next();

// Split the table by rows of 20 and build next/last functions to navigate.
var ofs = 0, pag = 20;
function display() {
    d3.select('#begin')
        .text(ofs);
    d3.select('#end')
        .text(ofs+pag-1);
    d3.select('#last')
        .attr('disabled', ofs-pag<0 ? 'true' : null);
    d3.select('#next')
        .attr('disabled', ofs+pag>=ndx.size() ? 'true' : null);
    d3.select('#size').text(ndx.size());
}

function update() {
    datatable.beginSlice(ofs);
    datatable.endSlice(ofs+pag);
    display();
}
function next() {
    ofs += pag;
    update();
    datatable.redraw();
}
function last() {
    ofs -= pag;
    update();
    datatable.redraw();
}


// Row chart function for single entry variables.
function barChart(uid, dim, color) {

    var Dim = ndx.dimension(function(d) {return d[dim];});
    var Group = Dim.group().reduceCount(function(d) {return d[dim];});

    var barChart  = dc.rowChart(uid);

    width = $(uid).width();
    height = $(uid).height() * .85;
    
    barChart
	    .width(width).height(height)
	    .dimension(Dim)
	    .group(Group)
        .cap(10)
        .ordering(function(d){ return -d.value })
        .colors(color)
        .title(function(d) { return ""; })
        .xAxis().ticks(10);
    dc.renderAll();
};

// Row chart function for list entry variables.
function barChartArray(uid, dim, color) {

    var Dim = ndx.dimension(function(d) {return d[dim];});
    var Group = Dim.groupAll().reduce(reduceAddArray(dim), reduceRemoveArray(dim), reduceInitial).value();

    Group.all = arrayGroupAll;
    Group.top =  arrayGroupTop;

    var barChart  = dc.rowChart(uid);

    var width = $(uid).width();
    var height = $(uid).height() * .85;

    barChart
	    .width(width).height(height)
	    .dimension(Dim)
	    .group(Group)
        .cap(10)
        .ordering(function(d){ return -d.value })
        .filterHandler(arrayFilterHandler)
        .colors(color)
        .xAxis().ticks(10);
    dc.renderAll();
}

// Submit search again to go back to the search result page.
$('#fallos-submit').on('click', function() {
    var q = $('#busqueda').text();
    $('#id_q').val(q);
    $('form').submit();
});

// FORCE LAYOUT CHART (SVG)
// Graph size.

function forceLayout() {

    var layout_width = $('#layout-subchart').width(),
        layout_height = $('#layout-subchart').height() * .9;
    
    // Toggle var for node/link opacity.
    var toggle = 0;
    
    // Scales values for zoom function.
    var xScale = d3.scale.linear()
            .domain([0, width])
            .range([0, width]);
    var yScale = d3.scale.linear()
            .domain([0, height])
            .range([0, height]);
    
    var zoomer = d3.behavior.zoom().x(xScale).y(yScale).scaleExtent([0.1, 8]);
    
    var color = d3.scale.category20();
    
    // Initiate force layout.
    var force = d3.layout.force()
        .gravity(0.2)
        .charge(-500)
        .linkDistance(50)
        .size([width, height]);
    
    // Append svg element to html.
    var svg = d3.select("#layout-subchart").append("svg")
        .attr("width", layout_width)
        .attr("height", layout_height);
    svg.call(zoomer);
    
    // Force config. Get node and link data from json graph var.
      force
          .nodes(graph.nodes)
          .links(graph.links)
          .start();
    
    
    // Load tootip function to display node name.
      var layouttip = d3.tip()
          .attr('class', 'd3-tip')
          .offset([-10, 0])
          .html(function(d) { return d.name; })
      svg.call(layouttip)

    // Append links and setup links details.
      var link = svg.selectAll(".link")
          .data(graph.links)
        .enter().append("line")
          .attr("class", "link")
          .style("stroke-width", function(d) { return Math.sqrt(d.value); });
    
    // Append nodes and setup nodes details.
      var node = svg.selectAll(".node")
          .data(graph.nodes)
          .enter().append("circle")
          .attr("class", "node")
          // .attr("r", function(d) {return d.weight * .5})
          .attr("r", 5)
          .style("fill", function(d) { return color(d.group); })
          .on('click', connectedNodes)
          .on('mouseover.layouttip', layouttip.show)
          .on('mouseout', layouttip.hide)
          .call(force.drag);
    
    // Append title to nodes.
    //  node.append("title")
    //      .text(function(d) { return d.name; });
    
    // Draw nodes and linnks on svg.
      force.on("tick", function() {
            link.attr("x1", function (d) { return  xScale(d.source.x); })
                .attr("y1", function (d) { return yScale(d.source.y);  })
                .attr("x2", function (d) { return xScale(d.target.x); })
                .attr("y2", function (d) { return yScale(d.target.y); });
    
            // Nodes with scale factors for zoom.
            node.attr("transform", function (d) {
                return "translate(" + xScale(d.x) + "," + yScale(d.y) + ")";
            });
                // .attr('r', function(d){return Math.sqrt(d.weight)});
      });

    // Index links and get neighboring nodes. This solution is form Mike Bostock in
    // http://stackoverflow.com/questions/8739072/highlight-selected-node-its-links-and-its-children-in-a-d3-force-directed-grap
    
    var linkedByIndex = {};
    for (i = 0; i < graph.nodes.length; i++) {
        linkedByIndex[i + "," + i] = 1;
    };
    
    graph.links.forEach(function (d) {
        linkedByIndex[d.source.index + "," + d.target.index] = 1;
     });
    
    function neighboring(a, b) {
        return linkedByIndex[a.index + "," + b.index];
    }
    
    // Function to highlight connected links and nodes.
    function connectedNodes() {
        if (toggle == 0) {
            d = d3.select(this).node().__data__;
            node.style("opacity", function (o) {
                    return neighboring(d, o) | neighboring(o, d) ?  1 : 0.15;
                    });
    
            link.style("opacity", function (o) {
                    return o.source === d || o.target === d ?  1 : 0.15;
                    });                                               
            toggle = 1;
        } else {
                node.style("opacity", 1);
                link.style("opacity", 1);
                toggle = 0;
            }
    }

};

function rowtips(){ 
    var tip = d3.tip()
        .attr('class', 'd3-tip')
        .offset([-10, 0])
        .html(function(d){return d.key;}) 
   
    d3.selectAll('g.row').call(tip); 
    d3.selectAll('g.row').on('mouseover', tip.show);

};

barChart("#main-chart", "corte", "#6a9bc3");
barChartArray("#main-right-chart", "jueces", "#6a9bc3");
barChartArray("#medium-left-chart", "citados", "#6a9bc3");
barChartArray("#medium-center-chart", "leyes", "#6a9bc3");
barChart("#bottom-left-chart", "sobre", "#6a9bc3");
barChartArray("#bottom-center-chart", "voces", "#6a9bc3");
barChartArray("#bottom-right-chart", "materia", "#6a9bc3");
mapChart();
forceLayout();
        
$('#network').on('click', function (){
    $('#map-subchart').hide()
    $('#layout-subchart').show()
        });

$('#map').on('click', function (){
    $('#map-subchart').show()
    $('#layout-subchart').hide()
        });

$(document).ready(function(){
    update();
    $('#layout-subchart').hide()
});

$('.close').on('click', function(){
        $(this).closest('.col-md-12').remove();
        });


</script>
</body>
{% endblock %}
