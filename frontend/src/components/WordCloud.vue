<template>
  <div>
    <v-card>
      <v-card-title>
        <!-- Dropdown for selecting country filter -->
        <!--<v-select
          :items="['All', 'Top 5', 'Worst 5']"
          label="Country Filter"
          v-model="selectedFilter"
          outlined
          dense
          class="dropdown"
        />-->
      </v-card-title>
      <!-- Word Cloud Visualization -->
      <div id="wordcloud" class="word-cloud"></div>
    </v-card>
  </div>
</template>

<script>
import axios from "axios";
import * as d3 from "d3";
import cloud from "d3-cloud";

export default {
  props: ["selectedYearRange"], // Receive the selected year range as a prop
  data() {
    return {
      wordData: [], // Stores word-frequency data
      selectedFilter: "All", // Default filter value
    };
  },
  watch: {
    selectedYearRange: {
      immediate: true, // Fetch data immediately on load
      handler() {
        this.fetchWordCloudData(); // Fetch data when the year range changes
      },
    },
    selectedFilter: {
      immediate: true, // React to filter changes
      handler() {
        this.fetchWordCloudData(); // Re-fetch data with the updated filter
      },
    },
  },
  methods: {
    async fetchWordCloudData() {
      try {
        console.log("Fetching word cloud data for year:", this.selectedYearRange, "with filter:", this.selectedFilter);
        const response = await axios.get("http://127.0.0.1:5000/api/word_cloud_filter", {
          params: { 
            yearRangeStart: this.selectedYearRange[0],
            yearRangeEnd: this.selectedYearRange[1],
            filter: this.selectedFilter, // Pass the selected filter
          },
        });
        this.wordData = response.data;

        // Debugging log
        console.log("Fetched Word Data:", this.wordData);

        if (this.wordData.length > 0) {
          this.renderWordCloud(); // Render the word cloud if data exists
        } else {
          console.warn("No word data available for the selected year");
          d3.select("#wordcloud").html("<p>No data available</p>");
        }
      } catch (error) {
        console.error("Error fetching word cloud data:", error);
      }
    },
    renderWordCloud() {
      console.log("Rendering Word Cloud...");

      // Get the container dimensions dynamically
      const containerWidth = document.getElementById("wordcloud").clientWidth || window.innerWidth;
      const containerHeight = document.getElementById("wordcloud").clientHeight || window.innerHeight * 0.275;

      // Clear any existing SVG
      const svg = d3.select("#wordcloud").html("").append("svg")
        .attr("width", containerWidth) // Adjust width to fit the container
        .attr("height", containerHeight); // Adjust height to fit the container

      // Map the word data to D3 format
      const words = this.wordData.map((d) => ({
        text: d.word,
        size: (Math.sqrt(d.count) * 30) / (this.selectedYearRange[1] - this.selectedYearRange[0] + 1), // Adjust scaling
      }));

      console.log("Mapped Words for Word Cloud:", words);

      const layout = cloud()
        .size([containerWidth, containerHeight]) // Match the SVG size
        .words(words) // Use the mapped words
        .padding(5) // Space between words
        .rotate(() => Math.random() > 0.5 ? 0 : 90) // Allow for varied rotation angles
        .fontSize((d) => d.size * 2) // Font size based on data
        .on("end", (words) => {
          console.log("Word Cloud Layout Complete:", words);
          this.drawWordCloud(words, svg, containerWidth, containerHeight);
        });

      layout.start();
    },

    drawWordCloud(words, svg, containerWidth, containerHeight) {
      console.log("Drawing Words:", words);

      // Calculate the center of the container
      const centerX = containerWidth / 2;
      const centerY = containerHeight / 2;

      // Create a group element and center it
      const g = svg.append("g")
        .attr("transform", `translate(${centerX},${centerY})`);

      // Add words to the visualization
      g.selectAll("text")
        .data(words)
        .enter().append("text")
        .style("font-size", (d) => `${d.size}px`)
        .style("fill", () => d3.schemeCategory10[Math.floor(Math.random() * 10)]) // Random colors
        .style("stroke", "black")
        .attr("text-anchor", "middle")
        .attr("transform", (d) => `translate(${d.x},${d.y})rotate(${d.rotate})`)
        .text((d) => d.text);

      console.log("Words successfully drawn");
    },

  },
};
</script>

<style scoped>
.word-cloud {
  height: 325px;
; /* Match the SVG height */
  width: 100%; /* Match the SVG width */
  margin: auto; /* Center the word cloud */
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f9f9f9; /* Light background for visibility */
}

.dropdown {
  width: 200px;
  margin-bottom: 16px;
}
</style>
