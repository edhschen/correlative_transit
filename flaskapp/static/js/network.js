var ridership_min = 2000;
var prep_data;
var height = 680, width = 800;

function chart(data){
  var color = d3.scaleOrdinal(d3.schemeTableau10);
  const links = data.links;
  const nodes = data.nodes;

  const simulation = d3.forceSimulation(Object.values(nodes))
      .force("link", d3.forceLink(links).id(d => d.id).distance(150))
      .force("charge", d3.forceManyBody().strength(-900))//.distanceMax
      .force('center', d3.forceCenter(width / 2, height / 2 - 30))
      //.force("collide", d3.forceCollide().radius(d => d.r + 1).iterations(3))
      .force("x", d3.forceX())
      .force("y", d3.forceY())
      .alphaTarget(1);

  const svg = d3.create("svg")
      .attr("width", width)
      .attr("height", height)
      //.attr("viewBox", [-width / 2, -height / 2, width, height])
      .style("font", "12px sans-serif");

  svg.append("defs").selectAll("marker")
    .data(links)
    .join("marker")
      .attr("id", `arrow`)
      .attr("viewBox", "0 -5 10 10")
      .attr("refX", 15)
      .attr("refY", -0.5)
      .attr("markerWidth", 6)
      .attr("markerHeight", 6)
      .attr("orient", "auto")
    .append("path")
      .attr("fill", "grey")
      .attr("d", "M0,-5L10,0L0,5");

  const link = svg.append("g")
      .attr("fill", "none")
      .attr("stroke-width", 1)
      .attr("opacity", 0.5)
    .selectAll("path")
    .data(links)
    .join("path")
      .attr("stroke", d => color(d.source.id))
      .attr("stroke-width", function(d) {return 0.1 + 1*(d.value/1000)})
    // .join("path")
    //   .attr("stroke-width", 1.5)
      // .attr("marker-end", d => `url(#arrow)`);

  const node = svg.append("g")
      .attr("fill", "currentColor")
      .attr("stroke-linecap", "round")
      .attr("stroke-linejoin", "round")
    .selectAll("g")
    .data(nodes)
    .join("g")
      .on("dblclick", function(d){
            d.fixed = false;
            d.fx = null;
            d.fy = null;
            d3.select(this).classed("fixed", false);
      })
      .call(drag(simulation));

  node.append("circle")
      .attr("stroke", "white")
      .attr("fill", d => {return color(d.id)})
      .attr("stroke-width", 1.5)
      .attr("r", function(d){return 5 + 0.25*(d.value/1000)});

  node.append("text")
      .attr("x", 8)
      .attr("y", "0.31em")
      .text(d => d.id)
    .clone(true).lower()
      .attr("fill", "none")
      .attr("stroke", "white")
      .attr("stroke-width", 3);

  simulation.on("tick", () => {
    link.attr("d", linkArc);
    node.attr("transform", d => `translate(${d.x},${d.y})`);
  });

  return svg.node();
}

drag = simulation => {

  function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  }

  function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
  }

  function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  }

  return d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended);
}

function linkArc(d) {
  const r = Math.hypot(d.target.x - d.source.x, d.target.y - d.source.y)*1.5;
  // console.log(r)
  return `
    M${d.source.x},${d.source.y}
    A${r},${r} 0 0,1 ${d.target.x},${d.target.y}
  `;
}

d3.text("static/bart/entry_exit_bart2.21_aggregated.csv").then(function(text) {
// CSV initial parse
// data format: [{exit_station, entry_stations: {station: entry_count}, exit_total}...]
prep_data = d3.csvParse(text.split('\n').slice(1).join(`\n`), function(d) {
  if (d["exit_station"] != ""){
    var entry_stations = Object.keys(d).filter((k) => !["", "Exits", "exit_station"]
      .includes(k)).reduce((res, k) => ({...res, [k]: parseInt(d[k].replace(' ', '').replace(',', ''))}), {});
    return {
      exit_station: d["exit_station"],
      entry_stations: entry_stations,
      exit_total: parseInt(d["Exits"].replace(' ', '').replace(',', ''))
    }
  }
});
console.log("LOADED DATA", prep_data)



// d3.csv()

function execgraph(){
  var station_names = prep_data.filter(d => d.exit_station != "Entries").map(d => d.exit_station)
  // console.log("STATION NAMES", station_names) 
  var ride_connections = [];
  var graphed_stations = [];
  // console.log(ridership_min)
  // console.log(typeof ridership_min)
  // console.log(prep_data, "PREP")
  // console.log("STATIONS ", station_names)
  station_names.forEach(entry_val => {
    // console.log(ridership_min)
    station_data = prep_data.filter(d => d.exit_station === entry_val)[0]
    // console.log("debug", station_data)
    var temp = Object.fromEntries(Object.entries(station_data.entry_stations).filter(([k,v]) => v >= ridership_min));
    // console.log("debug 2", temp)
    Object.entries(temp).forEach(([entry_station, ridership]) => {
      ride_connections.push({source: entry_station, target: station_data.exit_station, value: ridership})
    })
    // if (ride_connections[ride_connections.length - 1].target === station_data.exit_station){
    //   graphed_stations.push(station_data.exit_station)
    // }
  })
  // console.log(ride_connections)
  fin_data = ({nodes: Array.from(new Set(ride_connections.flatMap(l => [l.source, l.target])), id => ({id, value:ride_connections.filter(d => d.source == id).reduce(function (sum, curr) { return sum+curr.value },0)})), links: ride_connections})
  //fin_data =  {nodes: graphed_stations, links: ride_connections}
  // console.log("FILTERED CONNECTIONS", fin_data)

  graph = chart(fin_data)
  // console.log(graph)
  return graph
}

graph = execgraph()
curr = d3.select("#network")
   .append(() => graph);

d3.select("#ridership").on("input", function() {
  console.log("CHANGED to ", this.value)
  ridership_min = +this.value;
  curr.remove()
  graph = execgraph()
  curr = d3.select("#network")
    .append(() => graph)
});


// var width = 1200,
//     height = 700;
//
//  var force = d3.forceSimulation()
//      .nodes(Object.values(fin_data.nodes))
//      .force("link", d3.forceLink(fin_data.links).distance(100))
//      .force('center', d3.forceCenter(width / 2, height / 2))
//      .force("x", d3.forceX())
//      .force("y", d3.forceY())
//      .force("charge", d3.forceManyBody().strength(-250))
//      .alphaTarget(1);

});