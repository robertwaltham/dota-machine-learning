var d3 = require('d3');

module.exports = React.createClass({
  componentDidMount: function () {
    if (this.props.data) {
      this.d3RenderGraph(this.props.data);
    }
  },
  componentWillReceiveProps: function (props) {
    if (props.data) {
      this.d3RenderGraph(props.data);
    }
  },
  d3RenderGraph: function (data) {
    var margin = {top: 20, right: 20, bottom: 70, left: 40},
      width = 600 - margin.left - margin.right,
      height = 300 - margin.top - margin.bottom;

// Parse the date / time
    var parseDate = d3.time.format("%Y-%m").parse;

    var x = d3.scale.ordinal().rangeRoundBands([0, width], .05);

    var y = d3.scale.linear().range([height, 0]);

    var xAxis = d3.svg.axis()
      .scale(x)
      .orient("bottom")
      .tickFormat(d3.time.format("%b-%d"));

    var yAxis = d3.svg.axis()
      .scale(y)
      .orient("left")
      .ticks(10);

    var svg = d3.select("#graph").append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform",
      "translate(" + margin.left + "," + margin.top + ")");

    data.forEach(function (d) {
      d.date = new Date(d.date);
      d.value = +d.count;
    });

    x.domain(data.map(function (d) {
      return d.date;
    }));
    y.domain([0, d3.max(data, function (d) {
      return d.value;
    })]);

    svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis)
      .selectAll("text")
      .style("text-anchor", "end")
      .attr("dx", "-.8em")
      .attr("dy", "-.55em")
      .attr("transform", "rotate(-90)");

    svg.append("g")
      .attr("class", "y axis")
      .call(yAxis)
      .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("Matches");

    svg.selectAll("bar")
      .data(data)
      .enter().append("rect")
      .style("fill", "steelblue")
      .attr("x", function (d) {
        return x(d.date);
      })
      .attr("width", x.rangeBand())
      .attr("y", function (d) {
        return y(d.value);
      })
      .attr("height", function (d) {
        return height - y(d.value);
      });
  },
  render: function () {
    if (this.props.data) {
      return (
        <div id="graph"/>
      )
    } else {
      return (
        <div>No Data</div>
      )
    }
  }
});