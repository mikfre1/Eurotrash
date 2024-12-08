<template>
    <div>
      <v-card class="bar-chart-card">
        <div id="top5-placements-total-barchart" class="bar-chart-container"></div>
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
          const response = await axios.get("http://127.0.0.1:5000/api/top5barchartnormalized", {
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
        d3.select("#top5-placements-total-barchart").selectAll("*").remove();
  
        // Define dimensions and margin
        const margin = { top: 20, right: 70, bottom: 50, left: 150 };
        const containerWidth = document.getElementById("top5-placements-total-barchart").clientWidth;
        const heightPerBar = 40;
        const numBars = Object.keys(this.top5rankingData).length || 5; // Default to 5 if no data yet
        const height = heightPerBar * numBars + margin.top + margin.bottom;
  
        const width = containerWidth - margin.left - margin.right;
  
        // Append SVG element
        const svg = d3
          .select("#top5-placements-total-barchart")
          .append("svg")
          .attr("width", containerWidth)
          .attr("height", height)
          .append("g")
          .attr("transform", `translate(${margin.left},${margin.top})`);
  
        this.barchart = { svg, width, height, margin, heightPerBar };
      },
  
      updateBarChart() {
        if (!this.barchart || Object.keys(this.top5rankingData).length === 0) return;

        const { svg, width, heightPerBar } = this.barchart;

        // Prepare data and ensure `count` is parsed as a number
        const data = Object.entries(this.top5rankingData)
          .filter(([region]) => region !== "Unknown") // Exclude "Unknown" category
          .map(([region, count]) => ({
            region,
            count: parseFloat(count) * 100, // Convert to percentage
          }));

        // Sort data by count
        data.sort((a, b) => b.count - a.count);

        // Recalculate height based on the number of regions
        const numBars = data.length;
        const newHeight = heightPerBar * numBars + this.barchart.margin.top + this.barchart.margin.bottom;

        d3.select(svg.node().parentNode)
          .attr("height", newHeight);

        const yScale = d3
          .scaleBand()
          .domain(data.map((d) => d.region))
          .range([0, newHeight - this.barchart.margin.top - this.barchart.margin.bottom])
          .padding(0.1);

        const xScale = d3
          .scaleLinear()
          .domain([0, d3.max(data, (d) => d.count)]) // Use percentage values
          .range([0, width]);

        // Add X-axis
        svg
          .selectAll(".x-axis")
          .data([null])
          .join("g")
          .attr("class", "x-axis")
          .attr("transform", `translate(0, ${newHeight - this.barchart.margin.top - this.barchart.margin.bottom})`)
          .call(d3.axisBottom(xScale).ticks(5).tickFormat((d) => `${d}%`)) // Format ticks as percentages
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
                .attr("width", (d) => xScale(d.count))
                .attr("y", (d) => yScale(d.region))
                .attr("height", yScale.bandwidth()),
            (exit) => exit.remove()
          );

        // Add labels on bars
        svg
          .selectAll(".bar-label")
          .data(data, (d) => d.region) // Use the region name as the key
          .join(
            (enter) =>
              enter
                .append("text")
                .attr("class", "bar-label")
                .attr("x", (d) => xScale(d.count) + 10) // Place slightly to the right of the bar
                .attr("y", (d) => yScale(d.region) + yScale.bandwidth() / 2) // Center vertically
                .attr("dy", "0.35em") // Adjust for text alignment
                .style("fill", "#f8f9fa") // Label color
                .style("font-size", "12px") // Font size for labels
                .text((d) => `${d.count.toFixed(2)}%`), // Display value as percentage
            (update) =>
              update
                .transition()
                .duration(300)
                .attr("x", (d) => xScale(d.count) + 10) // Recalculate position for updated data
                .attr("y", (d) => yScale(d.region) + yScale.bandwidth() / 2) // Ensure correct alignment
                .text((d) => `${d.count.toFixed(2)}%`), // Ensure consistent format
            (exit) => exit.remove()
          );
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
  