<template>
  <div>
    <v-card class="line-graph-card">
      <div id="lineGraph" class="line-graph-container"></div>
    </v-card>
  </div>
</template>

<script>
import axios from "axios";
import * as d3 from "d3";

export default {
  props: {
    selectedCountries: {
      type: Array,
      default: () => ["Sweden", "Italy"], // Default value
    },
    selectedYearRange: {
      type: Array,
      required: true,
    },
  },
  data: () => ({
    rankingData: [], // Data for country dominance
    lineGraph: null, // To store the line graph configuration
  }),
  watch: {
    selectedCountries: {
      deep: true,
      handler() {
        this.updateLineGraph();
      },
    },
    selectedYearRange: {
      handler() {
        this.fetchRankingData();
      },
    },
  },
  mounted() {
    this.initializeLineGraph();
    this.fetchRankingData();
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.resize);
  },
  methods: {
    async fetchRankingData() {
      try {
        const response = await axios.get("http://127.0.0.1:5000/api/yearly_rankings", {
          params: {
            yearRangeStart: this.selectedYearRange[0],
            yearRangeEnd: this.selectedYearRange[1],
          },
        });
        this.rankingData = response.data;
        this.updateLineGraph();
      } catch (error) {
        console.error("Error fetching country data:", error);
      }
    },
    initializeLineGraph() {
      const margin = {top: 20, right: 20, bottom: 20, left: 20};
      const containerWidth = document.getElementById("lineGraph").clientWidth;
      const containerHeight = window.innerHeight * 0.275;

      const width = containerWidth - margin.left - margin.right;
      const height = containerHeight - margin.top - margin.bottom;

      const svg = d3
          .select("#lineGraph")
          .append("svg")
          .attr("width", width + margin.left + margin.right)
          .attr("height", height + margin.top + margin.bottom)
          .append("g")
          .attr("transform", `translate(${margin.left},${margin.top})`);

      this.lineGraph = {svg, margin, width, height};

      window.addEventListener("resize", this.resize);
    },
    resize() {
      if (!this.lineGraph) return;

      const containerWidth = document.getElementById("lineGraph").clientWidth;
      const containerHeight = window.innerHeight * 0.6;

      const width = containerWidth - this.lineGraph.margin.left - this.lineGraph.margin.right;
      const height = containerHeight - this.lineGraph.margin.top - this.lineGraph.margin.bottom;

      this.lineGraph.width = width;
      this.lineGraph.height = height;

      d3.select("#lineGraph svg")
          .attr("width", width + this.lineGraph.margin.left + this.lineGraph.margin.right)
          .attr("height", height + this.lineGraph.margin.top + this.lineGraph.margin.bottom);

      this.updateLineGraph();
    },
    drawAxis(type, scale, transform, ticks) {
      this.lineGraph.svg
          .selectAll(`.${type}-axis`)
          .data([0])
          .join("g")
          .attr("class", `${type}-axis`)
          .attr("transform", transform)
          .call(type === "x" ? d3.axisBottom(scale).ticks(ticks).tickFormat(d3.format("d")) : d3.axisLeft(scale).ticks(ticks))
          .selectAll("text")
          .attr("class", "axis-label")
          .style("fill", "#f8f9fa");
    },
    drawGrid(type, scale, ticks, size) {
      // Remove the domain line from the grid
      this.lineGraph.svg
          .selectAll(`.${type}-grid`)
          .data([0])
          .join("g")
          .attr("class", `${type}-grid`)
          .call(
              type === "x"
                  ? d3.axisBottom(scale).ticks(ticks).tickSize(-size).tickFormat("")
                  : d3.axisLeft(scale).ticks(ticks).tickSize(-size).tickFormat("")
          )
          .select(".domain")
          .remove(); // Remove the domain line
    }
    ,
    drawLegend(svg, countries, width) {
      
      svg.selectAll(".legend").remove();

      const legend = svg
          .selectAll(".legend")
          .data(countries)
          .join("g")
          .attr("class", "legend")
          .attr("transform", (_, i) => `translate(0, ${i * 20})`);

      legend
          .append("rect")
          .attr("x", width - 18)
          .attr("width", 18)
          .attr("height", 18)
          .style("fill", (_, i) => d3.schemeTableau10[i % 10]);

      legend
          .append("text")
          .attr("x", width - 24)
          .attr("y", 9)
          .attr("dy", ".35em")
          .style("text-anchor", "end")
          .text((d) => d)
          .style("fill", "#e0e0e0");
    },
    updateLineGraph() {
      if (!this.lineGraph) return;

      const {svg, width, height} = this.lineGraph;

      const xScale = d3.scaleLinear().range([0, width]);
      const yScale = d3.scaleLinear().range([0, height]);

      const filteredData = Object.keys(this.rankingData)
          .filter((country) => this.selectedCountries.includes(country))
          .reduce((obj, key) => {
            obj[key] = this.rankingData[key];
            return obj;
          }, {});

      const countries = Object.keys(filteredData);

      if (!countries.length) {
        d3.select("#lineGraph").html("<p>No data available</p>");
        return;
      }

      const years = Object.keys(filteredData[countries[0]]).map(Number);
      const yearRangeStart = Math.min(...years);
      const yearRangeEnd = Math.max(...years);

      xScale.domain([yearRangeStart, yearRangeEnd]);
      yScale.domain([0, d3.max(countries.flatMap((c) => Object.values(filteredData[c]))) + 1]);

      this.drawAxis("x", xScale, `translate(0, ${height})`, 5);
      this.drawAxis("y", yScale, "translate(0, 0)", 5);

      this.drawGrid("y", yScale, 4, width);



      svg
          .selectAll(".line")
          .data(
              countries.map((c) => ({
                country: c,
                values: Object.entries(filteredData[c])
                    .map(([year, rank]) => ({year: +year, rank: rank || null}))
                    .filter((d) => d.rank !== null),
              }))
          )
          .join("path")
          .attr("class", "line")
          .attr("fill", "none")
          .attr("stroke", (_, i) => d3.schemeTableau10[i % 10])
          .attr("stroke-width", 2)
          .attr("d", (d) =>
              d3
                  .line()
                  .x((d) => xScale(d.year))
                  .y((d) => yScale(d.rank))(d.values)
          );

      this.drawLegend(svg, countries, width);
    },
  },
};
</script>

<style scoped>
.line-graph-container {
  background-color: #4b4b4b;
  border-radius: 0; /* Remove rounded corners */
  padding: 10px;
  height: 30vh;
}

.axis-label {
  fill: #f8f9fa;
  font-size: 12px;
  font-weight: bold;
}

.grid-line {
  stroke: #6c757d;
  stroke-opacity: 0.6;
}

.line {
  stroke-width: 3;
  fill: none;
}
</style>
