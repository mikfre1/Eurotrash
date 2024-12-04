<template>
  <div>
    <v-card>
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
        this.fetchRankingData()},
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
      const margin = { top: 60, right: 50, bottom: 50, left: 50 };
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

      this.lineGraph = { svg, margin, width, height };

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
      updateLineGraph() {
        if (!this.lineGraph) return;

          const { svg, width, height } = this.lineGraph;

          // Define scales
          const xScale = d3.scaleLinear().range([0, width]);
          const yScale = d3.scaleLinear().range([height, 0]); // Invert y-axis

          // Filter rankingData for selected countries
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
          const totalYears = yearRangeEnd - yearRangeStart + 1;

          // Determine the interval dynamically based on the year range
          let interval = 5; // Default to 5 years
          if (totalYears > 50) interval = 10; // For long year ranges, increase the interval
          else if (totalYears < 20) interval = 2; // For shorter ranges, decrease the interval

          xScale.domain([yearRangeStart, yearRangeEnd]);
          yScale.domain([1, d3.max(countries.flatMap((c) => Object.values(filteredData[c]))) || 10]);

          // Generate aggregated data based on intervals
          const aggregatedData = countries.map((country) => {
            const rankings = Object.entries(filteredData[country])
              .map(([year, rank]) => ({ year: +year, rank }))
              .filter((d) => d.rank !== 0); // Skip points with rank = 0

            const groupedData = [];
            for (let i = yearRangeStart; i <= yearRangeEnd; i += interval) {
              const startYear = i;
              const endYear = Math.min(i + interval - 1, yearRangeEnd);

              const rangeRankings = rankings
                .filter((d) => d.year >= startYear && d.year <= endYear)
                .map((d) => d.rank);

              const avgRank = rangeRankings.length > 0
                ? rangeRankings.reduce((a, b) => a + b, 0) / rangeRankings.length
                : null;

              groupedData.push({
                year: startYear === yearRangeStart ? startYear : endYear, // Use exact year for the first point
                rank: startYear === yearRangeStart
                  ? rankings.find((d) => d.year === startYear)?.rank || null
                  : avgRank,
              });
            }

            return { country, values: groupedData.filter((d) => d.rank !== null) }; // Remove null ranks
          });

          // Define line generator
          const line = d3.line()
            .defined((d) => d.rank !== null && !isNaN(d.rank))
            .x((d) => xScale(d.year))
            .y((d) => yScale(d.rank));

          // Create axes
          const xAxis = d3.axisBottom(xScale).ticks(Math.ceil(totalYears / interval));
          const yAxis = d3.axisLeft(yScale);

          svg.selectAll(".x-axis").data([0]).join("g")
            .attr("class", "x-axis")
            .attr("transform", `translate(0, ${height})`)
            .call(xAxis);

          svg.selectAll(".y-axis").data([0]).join("g")
            .attr("class", "y-axis")
            .call(yAxis);

          // Draw lines
          svg.selectAll(".line").data(aggregatedData).join("path")
            .attr("class", "line")
            .attr("fill", "none")
            .attr("stroke", (_, i) => d3.schemeCategory10[i % 10])
            .attr("stroke-width", 2)
            .attr("d", (d) => line(d.values));
        },


  },
};
</script>

<style scoped>
.line-graph-container {
  width: 100%;
  height: 100%;
}
</style>
