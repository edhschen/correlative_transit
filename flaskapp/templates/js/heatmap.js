var debug;
var settings = {"rename": true, "normalized": false}
d3.json("cta-rides.json", function(d){
    // console.log(d)
}).then(function(data) {
    // functional definitions
    var timeParse = d3.timeParse("%s") // or new Date(+key)
    data = Object.entries(data).map(([key, val]) => {return ({"date": timeParse(+key/1000), "values": val})})
    // console.log(data)
    key_name = Object.keys(data[0].values)[0]
    if (key_name !== "exits") {
        settings.rename = true;
    }            
    data.forEach((d,i) => {
        if(settings.rename){
            data[i].values.exits = data[i].values[key_name] 
            delete data[i].values[key_name]
        }
        if(settings.normalized){
            var total = Object.values(data[i].values.exits).reduce((a,b) => a+b, 0)
            data[i].total = total
            Object.keys(data[i].values.exits).forEach(exit => {
                data[i].values.exits[exit] = data[i].values.exits[exit] / total
            })
        }
    })

    debug = data;
    stations = Array.from(new Set(data.flatMap(d => Object.keys(d.values.exits))))            
    proc_data = data.map(i => stations.map(station => i.values.exits[station] || 0)) // date first index by station second index
    proc_data = proc_data[0].map((_, colIndex) => proc_data.map(row => row[colIndex]));  // station first index ordered by date second index
    console.log(proc_data)
    console.log("Data", data, "Stations", stations)
    change_data = proc_data.map(station => station.map((x, i) => (station[i] - (station[i-1] || station[i]))/(station[i-1] || station[i]) ))
    console.log(change_data)

    // variable definitions
    var size = 16
    var width = size * data.length
    var innerHeight = size * stations.length
    var margin = {top: 70, right: 1, bottom: 40, left: 150}

    // axis and color scaling
    xScale = d3.scaleTime()
        .domain([d3.min(data, d => d.date), d3.max(data, d => d.date)])
        .rangeRound([margin.left, width - margin.right])
    yScale = d3.scaleBand()
        .domain(stations)
        .rangeRound([margin.top, margin.top + innerHeight])
    // console.log("xScale", xScale, "\nyScale", yScale)
    color = d3.scaleSequential([-1.5, 1.5], d3.interpolateRdBu)

    // define axis elements
    xAxis = g => g
        .attr("transform", `translate(0, ${margin.top})`)
        .call(d3.axisTop(xScale).tickFormat(d3.timeFormat("%B %d")))
        .call(g => g.select(".domain").remove())
    yAxis = g => g
        .attr("transform", `translate(${margin.left},0)`)
        .call(d3.axisLeft(yScale).tickSize(0))
        .call(g => g.select(".domain").remove())

    // append and defined main svg element
    const svg = d3.select("body").append("svg")
        .attr("width", width)
        .attr("height", innerHeight + margin.top + margin.bottom)
        // .attr("viewBox", [0, 0, width, innerHeight + margin.top + margin.bottom])
        .attr("font-family", "sans-serif")
        .attr("font-size", 10)
    
    // append and style additional required svg elements
    svg.append("g")
        .call(xAxis)
    svg.append("g")
        .call(yAxis)
    svg.append("g")
        .selectAll("g")
        .data(change_data)
        .join("g")
            .attr("transform", (d, i) => `translate(0,${yScale(stations[i])})`)
        .selectAll("rect")
        .data(d => d)
        .join("rect")
            .attr("x", (d, i) => {return xScale(data[i].date)})
            .attr("width", size)
            .attr("height", yScale.bandwidth() - 1)
            // .call(d => console.log(d))
            .attr("fill", (d, i) => {return isNaN(d) ? "#eee" : d === 0 ? "#fff" : color(d) })
    
    svg.append("g")
        .attr("class", "legendSeq")
        .attr("transform", "translate(150,20)")

    var legendSeq = d3.legendColor()
        .shapeWidth(40)
        .cells(15)
        .labelOffset(-30)
        .labelFormat(".2f")
        .orient("horizontal")
        .scale(color)
    
    svg.select(".legendSeq")
        .call(legendSeq);
});