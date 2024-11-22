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

    methods: {
      async fetchRankingData() {
        try {
          const response = await axios.get("http://127.0.0.1:5000/api/yearly_rankings", {
            params: { 
              yearRangeStart: this.selectedYearRange[0],
              yearRangeEnd: this.selectedYearRange[1]
            },
          });
          this.rankingData = response.data;
          this.updateLineGraph(); // Update map with new data
          /*Object.entries(this.rankingData).forEach(([country, years]) => {
            console.log("Country:", country, "Yearly Rankings:", years);
            }); --> debugging log */
        } catch (error) {
          console.error("Error fetching country data:", error);
        }
      },


      async initializeLineGraph() {
        // Clear any existing content in the container
        d3.select("#lineGraph").html("");

        // Set dimensions and margins
        const margin = { top: 60, right: 50, bottom: 50, left: 50 };
        const width = 1600 - margin.left - margin.right;
        const height = 500 - margin.top - margin.bottom;

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
      },

      updateLineGraph() {
        const { svg, width, height } = this.lineGraph;

        // Define scales
        const xScale = d3.scaleLinear().range([0, width]);
        const yScale = d3.scaleLinear().range([0, height]);

        // Filter rankingData for selected countries
        const data = this.rankingData;
        const filteredData = Object.keys(data)
            .filter((country) => this.selectedCountries.includes(country)) // Only include selected countries
            .reduce((obj, key) => {
            obj[key] = data[key];
            return obj;
            }, {});

        const countries = Object.keys(filteredData);

        // Get year range
        const years = Object.keys(data[countries[0]]).map(Number);
        const yearRangeStart = Math.min(...years);
        const yearRangeEnd = Math.max(...years);
        const rangeLength = yearRangeEnd - yearRangeStart;

        // Define step size
        let step;
        if (rangeLength >= 55 && rangeLength <= 65) step = 7;
        else if (rangeLength >= 45 && rangeLength <= 55) step = 5;
        else if (rangeLength >= 25 && rangeLength <= 45) step = 4;
        else if (rangeLength >= 15 && rangeLength <= 24) step = 3;
        else step = 1;

        // Group years by step and calculate averages
        const aggregatedData = countries.map((country) => {
            const rankings = years.map((year) => ({
            year,
            rank: data[country][year] || null, // Handle missing data
            }));

            const groupedData = [];
            groupedData.push({
            year: yearRangeStart,
            rank: data[country][yearRangeStart] || null, // Use the exact rank for the first year
            });
            for (let i = yearRangeStart + step; i <= yearRangeEnd; i += step) {
            const startYear = i - step + 1;
            const endYear = Math.min(i, yearRangeEnd);

            const rangeRankings = rankings
                .filter((d) => d.year >= startYear && d.year <= endYear)
                .map((d) => d.rank)
                .filter((r) => r !== null); // Exclude missing ranks

                const avgRank =
                    rangeRankings.length > 0
                        ? rangeRankings.reduce((a, b) => a + b, 0) / rangeRankings.length
                        : null; // Return null if no valid data


            groupedData.push({ year: endYear, rank: avgRank }); // Use end year for x-axis
            }

            return { country, values: groupedData };
        });

        // Update scales
        xScale.domain([yearRangeStart, yearRangeEnd]);
        const maxRank = Math.max(
            ...aggregatedData.flatMap((d) => d.values.map((v) => v.rank || 0))
        );
        yScale.domain([1, maxRank]); // 1 is the best rank

        // Create axes
        const xAxis = d3.axisBottom(xScale).tickValues(
            aggregatedData[0].values.map((d) => d.year) // Use aggregated years for x-axis ticks
        );
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
            .defined((d) => d.rank !== null && !isNaN(d.rank)) // Exclude invalid data points
            .x((d) => xScale(d.year))
            .y((d) => yScale(d.rank));

        // Bind data to paths and draw lines
        svg.selectAll(".line").data(aggregatedData).join("path")
            .attr("class", "line")
            .attr("fill", "none")
            .attr("stroke", (_, i) => d3.schemeCategory10[i % 10]) // Assign unique colors
            .attr("stroke-width", 2)
            .attr("d", (d) => line(d.values));

        // === Add the Legend ===
        const color = d3.scaleOrdinal(d3.schemeCategory10).domain(countries);

        const legend = svg.selectAll(".legend")
            .data(countries) // Bind the filtered list of countries
            .join(
                (enter) => enter.append("g").attr("class", "legend"), // Add new items
                (update) => update, // Update existing items
                (exit) => exit.remove() // Remove old items
            )
            .attr("transform", (_, i) => `translate(${i * 100}, -40)`); // Position legend at the top

            // Add or update color rectangles
            legend.selectAll("rect").data((d) => [d]).join(
            (enter) => enter.append("rect"),
            (update) => update,
            (exit) => exit.remove()
            )
            .attr("x", 0)
            .attr("y", 0)
            .attr("width", 18)
            .attr("height", 18)
            .style("fill", (d) => color(d));

            // Add or update text labels
            legend.selectAll("text").data((d) => [d]).join(
            (enter) => enter.append("text"),
            (update) => update,
            (exit) => exit.remove()
            )
            .attr("x", 24)
            .attr("y", 12) // Vertically align with the rectangle
            .attr("dy", ".35em")
            .style("text-anchor", "start")
            .text((d) => d);

        }


    }
}
  </script>
  
  <style scoped>

  .line-graph-container {
  width: 100%; /* Full width of the card */
  height: 700px; /* Adjust height as needed */
  position: relative;
  margin: 20px auto;
}
.widget-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.country-selector {
  display: flex;
  justify-content: space-between; /* Ensure equal spacing between selectors */
  padding: 0 20px; /* Add padding on both sides */
}
  
  </style>