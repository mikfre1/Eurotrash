<template>
  <div>
    <v-card>
      <v-card-title>
        <!-- Dropdown for selecting number of clusters -->
        <v-select
          :items="[3, 4, 5, 6]"
          label="Number of Clusters"
          v-model="numberOfClusters"
          outlined
          dense
          class="dropdown"
        />
      </v-card-title>
      <div id="scatterplot" class="scatterplot"></div>
    </v-card>
  </div>
</template>

<script>
import axios from "axios";
import * as d3 from "d3";

export default {
  props: ["selectedYearRange"], // Pass year range from parent
  data() {
    return {
      clusterData: [], // Data for the clusters
      numberOfClusters: 5, // Default number of clusters
    };
  },
  watch: {
    selectedYearRange: {
      immediate: true, // Fetch data immediately on mount
      handler() {
        this.fetchClusterData();
      },
    },
    numberOfClusters: {
      immediate: true, // React immediately to cluster count changes
      handler(newCount) {
        console.log("Cluster count emitted:", this.numberOfClusters);
        this.$emit("cluster-count-updated", newCount);
        this.fetchClusterData();
      },
    },
  },
  methods: {
    
    async fetchClusterData() {
      try {
        const response = await axios.get("http://127.0.0.1:5000/api/voting_clusters", {
          params: {
            yearRangeStart: this.selectedYearRange[0],
            yearRangeEnd: this.selectedYearRange[1],
            numberOfClusters: this.numberOfClusters, // Pass selected number of clusters
          },
        });
        this.clusterData = response.data;
        this.drawScatterPlot(); // Render the visualization
      } catch (error) {
        console.error("Error fetching cluster data:", error);
      }
    },
    drawScatterPlot() {
      const width = 800;
      const height = 600;

      // Clear existing visualization
      d3.select("#scatterplot").selectAll("*").remove();

      // Create SVG
      const svg = d3.select("#scatterplot")
        .append("svg")
        .attr("width", width)
        .attr("height", height);

      // Define scales
      const xScale = d3.scaleLinear()
        .domain(d3.extent(this.clusterData, (d) => d.x))
        .range([50, width - 50]); // Add padding
      const yScale = d3.scaleLinear()
        .domain(d3.extent(this.clusterData, (d) => d.y))
        .range([height - 50, 50]); // Invert y-axis for correct orientation

      // Add circles for each data point
      svg.selectAll("circle")
        .data(this.clusterData)
        .enter()
        .append("circle")
        .attr("cx", (d) => xScale(d.x))
        .attr("cy", (d) => yScale(d.y))
        .attr("r", 12) // Circle size
        .attr("fill", (d) => d3.schemeCategory10[d.cluster % 10]) // Cluster-based color
        .attr("opacity", 0.8);

      // Add country labels
      svg.selectAll("text")
        .data(this.clusterData)
        .enter()
        .append("text")
        .attr("x", (d) => xScale(d.x) + 12) // Offset from circle
        .attr("y", (d) => yScale(d.y))
        .attr("font-size", "20px")
        .attr("fill", "black")
        .text((d) => d.country);
    },
  },
};
</script>

<style scoped>
.scatterplot {
  height: 600px;
  width: 800px;
  margin: auto;
}
.dropdown {
  width: 200px;
  margin-bottom: 16px;
}
</style>
