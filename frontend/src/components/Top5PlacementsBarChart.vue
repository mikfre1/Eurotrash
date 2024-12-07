<template>
    <div>
      <v-card class="bar-chart-card">
        <div id="top5-placements-barchart" class="bar-chart-container"></div>
      </v-card>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  import * as d3 from "d3";
  
  export default {
    props: {
      selectedYearRange: {
        type: Array,
        required: true,
      },
    },
    data: () => ({
      top5rankingData: {}, // Data for top 5 rankings
    }),
    watch: {
      selectedYearRange: {
        handler() {
          this.fetchtop5RankingData();
        },
      },
    },
    mounted() {
      this.initializeBarChart();
      this.fetchtop5RankingData();
    },
    methods: {
      async fetchtop5RankingData() {
        try {
          const response = await axios.get("http://127.0.0.1:5000/api/top5barchart", {
            params: {
              yearRangeStart: this.selectedYearRange[0],
              yearRangeEnd: this.selectedYearRange[1],
            },
          });
          this.top5rankingData = response.data;
          this.updateBarChart();
        } catch (error) {
          console.error("Error fetching top 5 ranking data:", error);
        }
      },
  
      initializeBarChart() {
        // Clear previous chart
        d3.select("#top5-placements-barchart").selectAll("*").remove();
  
        // Define dimensions and margin
        const margin = { top: 20, right: 20, bottom: 50, left: 150 };
        const containerWidth = document.getElementById("top5-placements-barchart").clientWidth;
        const heightPerBar = 40;
        const numBars = Object.keys(this.top5rankingData).length || 5; // Default to 5 if no data yet
        const height = heightPerBar * numBars + margin.top + margin.bottom;
  
        const width = containerWidth - margin.left - margin.right;
  
        // Append SVG element
        const svg = d3
          .select("#top5-placements-barchart")
          .append("svg")
          .attr("width", containerWidth)
          .attr("height", height)
          .append("g")
          .attr("transform", `translate(${margin.left},${margin.top})`);
  
        this.barchart = { svg, width, height, margin, heightPerBar };
      },
  
      updateBarChart() {
        if (!this.barchart || Object.keys(this.top5rankingData).length === 0) return;

        const { svg, width, height, heightPerBar } = this.barchart;

        // Prepare data and ensure `count` is parsed as a number
        const data = Object.entries(this.top5rankingData)
            .filter(([region]) => region !== "Unknown") // Exclude "Unknown" category
            .map(([region, count]) => ({
            region,
            count: parseInt(count, 10), // Parse `count` as an integer
            }));

        // Sort data by count
        data.sort((a, b) => b.count - a.count);

        // Update scales
        const yScale = d3
            .scaleBand()
            .domain(data.map((d) => d.region))
            .range([0, height - heightPerBar]) // Adjust for the total height
            .padding(0.1);

        const xScale = d3
            .scaleLinear()
            .domain([0, d3.max(data, (d) => d.count)]) // Use parsed `count` values
            .range([0, width]);

        // Add X-axis
        svg
            .selectAll(".x-axis")
            .data([null])
            .join("g")
            .attr("class", "x-axis")
            .attr("transform", `translate(0, ${height - heightPerBar})`)
            .call(d3.axisBottom(xScale).ticks(5))
            .selectAll("text")
            .style("fill", "#f8f9fa");

        // Add Y-axis
        svg
            .selectAll(".y-axis")
            .data([null])
            .join("g")
            .attr("class", "y-axis")
            .call(d3.axisLeft(yScale))
            .selectAll("text")
            .style("fill", "#f8f9fa");

        // Draw bars
        svg
            .selectAll(".bar")
            .data(data, (d) => d.region)
            .join(
            (enter) =>
                enter
                .append("rect")
                .attr("class", "bar")
                .attr("y", (d) => yScale(d.region))
                .attr("height", yScale.bandwidth())
                .attr("x", 0)
                .attr("width", (d) => xScale(d.count))
                .attr("fill", "#17a2b8"),
            (update) =>
                update
                .transition()
                .duration(300)
                .attr("width", (d) => xScale(d.count)),
            (exit) => exit.remove()
            );

        // Remove labels on bars
        svg.selectAll(".bar-label").remove();
        },


    },
  };
  </script>
  
  <style scoped>
  .bar-chart-container {
    background-color: #4b4b4b;
    border-radius: 0;
    padding: 10px;
  }
  
  .axis-label {
    fill: #f8f9fa;
    font-size: 12px;
    font-weight: bold;
  }
  
  .bar {
    transition: fill 0.3s ease;
  }
  
  .bar:hover {
    fill: #138496; /* Slightly darker shade on hover */
  }
  </style>
  