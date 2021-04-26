var debug;
var settings = {"rename": false, "normalized": false, "type": "count"}
function genviz(filepath){
    d3.json(`static/info/${filepath}.json`, function(d){
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
        if (settings.type === "change"){
            change_data = proc_data.map(station => station.map((x, i) => (station[i] - (station[i-1] || station[i]))/(station[i-1] || station[i]) ))
            console.log(change_data)
            proc_data = change_data;
        }

        // variable definitions
        var size = Math.max(5, 900/stations.length)
        var width = 1000
        var innerHeight = size * stations.length
        var margin = {top: 70, right: 1, bottom: 40, left: 50}

        // axis and color scaling
        xScale = d3.scaleTime()
            .domain([d3.min(data, d => d.date), d3.max(data, d => d.date)])
            .rangeRound([margin.left, width - margin.right])
        yScale = d3.scaleBand()
            .domain(stations)
            .rangeRound([margin.top, margin.top + innerHeight])
        // console.log("xScale", xScale, "\nyScale", yScale)
        ranges = {"count": [0, d3.max(data, d => d3.max(Object.values(d.values.exits)))], "change": [-1.5, 1.5]}
        scales = {"count": d3.interpolateBlues, "change": d3.interpolateRdBu}
        color = d3.scaleSequentialSqrt(ranges[settings.type], scales[settings.type])

        // define axis elements
        xAxis = g => g
            .attr("transform", `translate(0, ${margin.top})`)
            .call(d3.axisTop(xScale).tickFormat(d3.timeFormat("%B %d")))
            .call(g => g.select(".domain").remove())
        yAxis = g => g
            .attr("transform", `translate(${margin.left},0)`)
            .style("font-size", Math.min(size, 8))
            .call(d3.axisLeft(yScale).tickSize(0))
            .call(g => g.select(".domain").remove())

        // append and defined main svg element
        const svg = d3.select("#heatmap").append("svg")
            .attr("width", width)
            .attr("height", innerHeight + margin.top + margin.bottom)
            // .attr("viewBox", [0, 0, width, innerHeight + margin.top + margin.bottom])
            .attr("font-family", "sans-serif")
            .attr("font-size", 5)
        
        // append and style additional required svg elements
        svg.append("g")
            .call(xAxis)
        svg.append("g")
            .call(yAxis)
        svg.append("g")
            .selectAll("g")
            .data(proc_data)
            .join("g")
                .attr("transform", (d, i) => `translate(0,${yScale(stations[i])})`)
            .selectAll("rect")
            .data(d => d)
            .join("rect")
                .attr("x", (d, i) => {return xScale(data[i].date)})
                .attr("width", width/data.length)
                .attr("height", yScale.bandwidth() - 1)
                // .call(d => console.log(d))
                .attr("fill", (d, i) => {return isNaN(d) ? "#eee" : d === 0 ? "#fff" : color(d) })
        
        svg.append("g")
            .attr("class", "legendSeq")
            .attr("transform", `translate(${width/6 + 10},20)`)

        labelformats = {"count" : d3.format("d"), "change": ".2f"}
        var legendSeq = d3.legendColor()
            .shapeWidth(40)
            .cells(15)
            .labelOffset(-30)
            .labelFormat(!settings.normalized ? labelformats[settings.type] : ".4f")
            .orient("horizontal")
            .scale(color)
        
        svg.select(".legendSeq")
            .call(legendSeq);
    });
}

genviz("sfbay-bart-exits")

datafilemap = {
    "SF Bay Bart 2021": "sfbay-bart-exits",
    "Chicago Metro 2020": "cta-rides-2020",
    "NYC MTA 2019": "mta-exits-2019",
    "NYC MTA 2020": "mta-exits-2020",
    "NYC MTA 2021": "mta-exits-2021"
}

d3.select("#heat_data").on("change", function() {
    console.log("CHANGED to", d3.select(this).property("value"))
    d3.select("#heatmap").selectAll("svg").remove()
    genviz(d3.select(this).property("value"));
});

d3.select("#heat_norm").on("change", function() {
    if (d3.select(this).property("checked")) {
        settings.normalized = true;
    } else {
        settings.normalized = false;
    }
    d3.select("#heatmap").selectAll("svg").remove()
    genviz(d3.select("#heat_data").property("value"))
})

d3.select("#heat_type").on("change", function() {
    console.log("CHANGED to", d3.select(this).property("value"))
    d3.select("#heatmap").selectAll("svg").remove()
    settings.type = d3.select(this).property("value")
    genviz(d3.select("#heat_data").property("value"));
});