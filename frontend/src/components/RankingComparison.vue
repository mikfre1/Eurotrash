<template>
  <div>
    <v-card>
      <div class="widget-header">
        <div class="control-panel-font"></div>
        <v-row class="country-selector">
          <v-col cols="6">
            <v-select
              :items="availableCountries"
              v-model="selectedCountries[0]"
              label="Country 1"
              dense
              outlined
            ></v-select>
          </v-col>
          <v-col cols="6">
            <v-select
              :items="availableCountries"
              v-model="selectedCountries[1]"
              label="Country 2"
              dense
              outlined
            ></v-select>
          </v-col>
        </v-row>
      </div>
      <div id="lineGraph" class="line-graph-container"></div>
    </v-card>
  </div>
</template>

<script>
import axios from "axios";
import * as d3 from "d3";

export default {
  props: ["selectedYearRange"],
  data: () => ({
    rankingData: [], // Data for country dominance
    selectedCountries: ["Sweden", "Italy"],
  }),

  computed: {
    // Dynamically get available countries based on rankingData
    availableCountries() {
      return Object.keys(this.rankingData);
    },
  },

  watch: {
    selectedCountries: {
      deep: true, // Watch for changes in the array
      handler() {
        this.updateLineGraph();
      },
    },
    selectedYearRange: {
      immediate: true, // Fetch data on initial load
      handler() {
        this.fetchRankingData(); // Fetch new data
      },
    },
  },

  mounted() {
    if (this.availableCountries.length >= 2) {
      this.selectedCountries = [this.availableCountries[0], this.availableCountries[1]];
    }
    this.initializeLineGraph();
    this.fetchRankingData();
  },

  beforeUnmount() {
    // Remove resize listener when component is destroyed
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
        this.updateLineGraph(); // Update graph with new data
      } catch (error) {
        console.error("Error fetching country data:", error);
      }
    },

    async initializeLineGraph() {
      // Clear any existing content in the container
      d3.select("#lineGraph").html("");

      // Set dimensions and margins dynamically
      const margin = { top: 60, right: 50, bottom: 50, left: 50 };
      const containerWidth = document.getElementById("lineGraph").clientWidth || window.innerWidth;
      const containerHeight = window.innerHeight * 0.275;

      const width = containerWidth - margin.left - margin.right;
      const height = containerHeight - margin.top - margin.bottom;

      // Append the SVG element to the container
      const svg = d3
        .select("#lineGraph")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

      // Store the SVG and dimensions for later use in updateLineGraph
      this.lineGraph = { svg, margin, width, height };

      // Add resize listener
      window.addEventListener("resize", this.resize);
    },

    resize() {
      // Recalculate dimensions
      const containerWidth = document.getElementById("lineGraph").clientWidth || window.innerWidth;
      const containerHeight = window.innerHeight * 0.6;

      const width = containerWidth - this.lineGraph.margin.left - this.lineGraph.margin.right;
      const height = containerHeight - this.lineGraph.margin.top - this.lineGraph.margin.bottom;

      // Update the stored dimensions
      this.lineGraph.width = width;
      this.lineGraph.height = height;

      // Update the SVG element's size
      d3.select("#lineGraph svg")
        .attr("width", width + this.lineGraph.margin.left + this.lineGraph.margin.right)
        .attr("height", height + this.lineGraph.margin.top + this.lineGraph.margin.bottom);

      // Redraw the graph with the new dimensions
      this.updateLineGraph();
    },

    updateLineGraph() {
      const { svg, width, height } = this.lineGraph;

      // Define scales
      const xScale = d3.scaleLinear().range([0, width]);
      const yScale = d3.scaleLinear().range([height, 0]);

      // Filter rankingData for selected countries
      const data = this.rankingData;
      const filteredData = Object.keys(data)
        .filter((country) => this.selectedCountries.includes(country))
        .reduce((obj, key) => {
          obj[key] = data[key];
          return obj;
        }, {});

      const countries = Object.keys(filteredData);

      // Get year range
      const years = Object.keys(data[countries[0]]).map(Number);
      const yearRangeStart = Math.min(...years);
      const yearRangeEnd = Math.max(...years);

      // Define step size
      const step = 5; // Example step size

      // Group years by step and calculate averages
      const aggregatedData = countries.map((country) => {
        const rankings = years.map((year) => ({
          year,
          rank: data[country][year] || null, // Handle missing data
        }));

        const groupedData = [];
        for (let i = yearRangeStart; i <= yearRangeEnd; i += step) {
          const startYear = i;
          const endYear = Math.min(i + step - 1, yearRangeEnd);

          const rangeRankings = rankings
            .filter((d) => d.year >= startYear && d.year <= endYear)
            .map((d) => d.rank)
            .filter((r) => r !== null);

          const avgRank =
            rangeRankings.length > 0
              ? rangeRankings.reduce((a, b) => a + b, 0) / rangeRankings.length
              : null;

          groupedData.push({ year: endYear, rank: avgRank });
        }

        return { country, values: groupedData };
      });

      // Update scales
      xScale.domain([yearRangeStart, yearRangeEnd]);
      const maxRank = Math.max(
        ...aggregatedData.flatMap((d) => d.values.map((v) => v.rank || 0))
      );
      yScale.domain([1, maxRank]);

      // Create axes
      const xAxis = d3.axisBottom(xScale);
      const yAxis = d3.axisLeft(yScale);

      svg.selectAll(".x-axis").data([0]).join("g")
        .attr("class", "x-axis")
        .attr("transform", `translate(0, ${height})`)
        .call(xAxis);

      svg.selectAll(".y-axis").data([0]).join("g")
        .attr("class", "y-axis")
        .call(yAxis);

      // Define line generator
      const line = d3.line()
        .defined((d) => d.rank !== null && !isNaN(d.rank))
        .x((d) => xScale(d.year))
        .y((d) => yScale(d.rank));

      // Bind data to paths and draw lines
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
  position: relative;
}
.widget-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.country-selector {
  display: flex;
  justify-content: space-between;
  padding: 0 20px;
}
</style>
