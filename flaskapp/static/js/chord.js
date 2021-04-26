// // var svg = d3.select("#container")
// //   .append("svg")
// //     .attr("width", 800)
// //     .attr("height", 800)
// //   .append("g")
// //     .attr("transform", "translate(400,400)")

// var ground = []; // Initialize array
// for (var i = 0 ; i < 10; i++) {
//     ground[i] = []; // Initialize inner array
//     for (var j = 0; j < 10; j++) { // i++ needs to be j++
//         ground[i][j] = (Math.random() * 10 | 0);
//     }
// }

// // create a matrix
// var matrix = [
//   [0,  5871, 8916, 2868],
//   [ 1951, 0, 2060, 6171],
//   [ 8010, 16145, 0, 8045],
//   [ 1013,   990,  940, 0],
// ];

// // 4 groups, so create a vector of 4 colors
var colors = [ "#440154ff", "#31668dff", "#37b578ff", "#fde725ff"]
var colors_alt = d3.scaleOrdinal(d3.schemeTableau10)

// // give this matrix to d3.chord(): it will calculates all the info we need to draw arc and ribbon
// var res = d3.chord()
//     .padAngle(0.05)
//     .sortSubgroups(d3.descending)
//     (ground)

// // add the groups on the outer part of the circle
// svg
//   .datum(res)
//   .append("g")
//   .selectAll("g")
//   .data(function(d) { return d.groups; })
//   .enter()
//   .append("g")
//   .append("path")
//     .style("fill", function(d,i){ return colors_alt(i) })
//     .style("stroke", "none")
//     .attr("d", d3.arc()
//       .innerRadius(380)
//       .outerRadius(400)
//     )

// // Add the links between groups
// svg
//   .datum(res)
//   .append("g")
//   .selectAll("path")
//   .data(function(d) { return d; })
//   .enter()
//   .append("path")
//     .attr("d", d3.ribbonArrow().radius(380).padAngle(1 / 400))
//     .style("fill", function(d){ return(colors_alt(d.source.index)) })
//     .style("opacity", "0.7")
//     .style("mix-blend-mode", "multiply");

// svg.attr("display", "none");

// d3.text("entry_exit_bart21.csv").then(function(text) {
//   text = "date,entry_hour,entry_station,exit_station,exit_hour\n" + text;
//   var data = d3.csvParse(text, function(d) {
//     return {
//       entry_time: d3.timeParse("%Y-%m-%d-%H")(d.date + "-" + d.entry_hour),
//       exit_time: d3.timeParse("%Y-%m-%d-%H")(d.date + "-" + d.exit_hour),
//       entry_station: d.entry_station,
//       exit_station: d.exit_station
//     }
//   });
//   console.log(data)
// });
// var svg;
d3.text("static/bart/entry_exit_bart2.21_aggregated.csv").then(function(text) {
  // CSV initial parse
  // data format: [{exit_station, entry_stations: {station: entry_count}, exit_total}...]
  var data = d3.csvParse(text.split('\n').slice(1).join(`\n`), function(d) {
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

  console.log("LOADED DATA", data)
  all_station_names = data.filter(d => d.exit_station != "Entries").map(d => d.exit_station)
  console.log("STATION NAMES", all_station_names)
  //station_names = ["BK", "AS", "WS", "FM", "ML", "BE", "MT", "SL", "PL"]

  function gen_chord(num){
    const shuffled = all_station_names.sort(() => 0.5 - Math.random());
    var station_names = shuffled.slice(0, num)
    console.log(station_names)

    // entry/exit matrix formation
    // data format: station_names by station_names, primary index is by exit station, secondary index is by entry station
    // eg. 3rd array's 2nd element is the throughput of passengers traveling from the 2nd station to the 3rd station as ref. to station_names
    var data_matrix = [];
    station_names.forEach(entry_val => {
      matrix_add = data.filter(d => d.exit_station === entry_val)[0]
      data_matrix.push(station_names.map(station_name => matrix_add.entry_stations[station_name] || 0))
    })

    console.log(data_matrix)

    data_matrix = data_matrix[0].map((_, colIndex) => data_matrix.map(row => row[colIndex]));

    data_matrix[0].forEach((k,i) => {
      data_matrix[i][i] = 0
    })

    var svg = d3.select("#chord")
      .append("svg")
        .attr("width", 820)
        .attr("height", 820)
      .append("g")
        .attr("transform", "translate(410,410)")

    console.log(svg)

    var res = d3.chordDirected()
        .padAngle(0.05)
        .sortSubgroups(d3.ascending)
        (data_matrix)

    // add the groups on the outer part of the circle
    // svg
    //   .datum(res)
    //   .append("g")
    //   .selectAll("g")
    //   .data(function(d) { return d.groups; })
    //   .enter()
    //   .append("g")
    //   .append("path")
    //     .style("fill", function(d,i){ return colors_alt(i) })
    //     //.style("stroke", "red")
    //     .attr("d", d3.arc()
    //       .innerRadius(700)
    //       .outerRadius(750)
    //     )

    // Add the links between groups
    // const textId = DOM.uid("text");
    // svg
    //     .append("path")
    //     .attr("id", textId.id)
    //     .attr("fill", "none")
    //     .attr("d", d3.arc()({750, startAngle: 0, endAngle: 2 * Math.PI}));
    // console.log(data_matrix[26].reduce((a,b) => a+b,0))
    // console.log(data_matrix.reduce((a,b) => a+b[26],0))

    function focusin(s_focus) {
      console.log("exec")
      d3.selectAll(".ribbons")
        .style("opacity", function(d) {return "0.03"})
      d3.selectAll(".r"+s_focus)
        .style("opacity", "1")
    }

    function focusout() {
      d3.selectAll(".ribbons")
        .style("opacity", function(d) { return "0.5"})
    }

    var woa = svg
      .datum(res)
      .append("g")
      .selectAll("path")

      woa.data(function(d) {return d;})
        .enter()
        .append("path")
        //.data(function(d) {console.log(d)})
        // .attr("class", function(d) {console.log(d)})
        .attr("d", d3.ribbonArrow().radius(350).padAngle(0).headRadius(15))
        .style("fill", function(d){ return(colors_alt(d.source.index)) })
        .attr("class", function(d){
          if ((station_names[d.source.index] == "AS") & (station_names[d.target.index] == "BK")){
            //extra = "interest"
            return "ribbons r" + station_names[d.source.index] + " interest"
          }
          return "ribbons r" + station_names[d.source.index]
        })
        .style("opacity", ".5")
        .style("mix-blend-mode", "multiply");

      // woa.data(function(d) { return d; })
      //   .enter()
      //   .append("path")
      //   .attr("class", function(d) {console.log(d)})
      //   .attr("d", d3.ribbonArrow().radius(700).padAngle(0).headRadius(30))
      //   .style("fill", function(d){ return(colors_alt(d.source.index)) })
      //   .attr("class", function(d){
      //     if ((station_names[d.source.index] == "AS") & (station_names[d.target.index] == "BK")){
      //       //extra = "interest"
      //       return "ribbons r" + station_names[d.source.index] + " interest"
      //     }
      //     return "ribbons r" + station_names[d.source.index]
      //   })
      //   .style("opacity", ".5")
      //   .style("mix-blend-mode", "multiply");

      // woa.append("path")
      //   .attr("class", function(d) {console.log(d)})
      //   .attr("d", function(d) {
      //     temp = d.source
      //     d.source = d.target
      //     d.target = temp
      //     return d3.ribbonArrow().radius(700).padAngle(0).headRadius(30)
      //   })
      //   .style("fill", function(d){ return(colors_alt(d.source.index)) })
      //   .attr("class", function(d){
      //     if ((station_names[d.source.index] == "AS") & (station_names[d.target.index] == "BK")){
      //       //extra = "interest"
      //       return "ribbons r" + station_names[d.source.index] + " interest"
      //     }
      //     return "ribbons r" + station_names[d.source.index]
      //   })
      //   .style("opacity", ".5")
      //   .style("mix-blend-mode", "multiply");



    svg.append("g")
      .attr("font-family", "sans-serif")
      .attr("font-size", 12)
    .selectAll("g")
    .data(res.groups)
    .join("g")
      .call(g => g.append("path")
        .attr("d", d3.arc()
          .innerRadius(350)
          .outerRadius(375))
        .attr("fill", d => colors_alt(d.index)))
        .on("mouseover", function(d) {focusin(station_names[d3.select(this).datum().index])})
        .on("mouseout", function(d) {focusout()})
      .call(g => g.append("text")
        .attr('transform', function (d) {
          return 'translate(' +
            d3.arc()
              .innerRadius(350)
              .outerRadius(375).startAngle(d.startAngle)
            .endAngle(d.endAngle)
            .centroid() // this is an array, so will automatically be printed out as x,y
            + ')'
        })
        .attr('text-anchor', 'middle')
        .attr("startOffset", d => d.startAngle * 750)
        .style("user-select", "none")
        .text(d => station_names[d.index]))
  }
  gen_chord(20)

  d3.select("#chord_in").on("input", function() {
    console.log("CHANGED to", +this.value)
    d3.select("#chord").selectAll("svg").remove()
    gen_chord(+this.value);
  });



})
