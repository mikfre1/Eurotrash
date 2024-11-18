<template>
    <div>
      <v-card>
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
    props: ["selectedYear"], // Receive the selected year as a prop
    data() {
      return {
        wordData: [], // Stores word-frequency data
      };
    },
    watch: {
      selectedYear: {
        immediate: true, // Fetch data immediately on load
        handler(newYear) {
          this.fetchWordCloudData(newYear); // Fetch data when the year changes
        },
      },
    },
    methods: {
      async fetchWordCloudData(year) {
        try {
          console.log("Fetching word cloud data for year:", year);
          const response = await axios.get("http://127.0.0.1:5000/api/word_cloud", {
            params: { year },
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
  
        // Clear any existing SVG
        const svg = d3.select("#wordcloud").html("").append("svg")
          .attr("width", 375) // Adjust width to fit the container
          .attr("height", 300); // Adjust height to fit the container
  
        // Map the word data to D3 format
        const words = this.wordData.map((d) => ({
          text: d.word,
          size: Math.sqrt(d.count) * 5, // Scale the size (adjust as needed)
        }));
  
        // Debugging log
        console.log("Mapped Words for Word Cloud:", words);
  
        const layout = cloud()
          .size([375, 300]) // Match the SVG size
          .words(words) // Use the mapped words
          .padding(5) // Space between words
          .rotate(() => (Math.random() > 0.5 ? 0 : 90)) // Random rotation for variety
          .fontSize((d) => d.size) // Font size based on scaled count
          .on("end", (words) => {
            console.log("Word Cloud Layout Complete:", words); // Debugging log
            this.drawWordCloud(words, svg);
          });
  
        layout.start();
      },
      drawWordCloud(words, svg) {
        console.log("Drawing Words:", words);

        // Get the SVG dimensions
        const svgWidth = parseInt(svg.attr("width"));
        const svgHeight = parseInt(svg.attr("height"));

        // Dynamically calculate the center of the SVG
        const centerX = svgWidth / 2;
        const centerY = svgHeight / 2;

        // Append and center the word cloud
        const g = svg.append("g")
            .attr("transform", `translate(${centerX},${centerY})`); // Center dynamically

        g.selectAll("text")
            .data(words)
            .enter().append("text")
            .style("font-size", (d) => `${d.size}px`)
            .style("fill", () => d3.schemeCategory10[Math.floor(Math.random() * 10)]) // Random colors
            .style("stroke", "black") // Add stroke for better visibility
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
    height: 300px; /* Match the SVG height */
    width: 375px; /* Match the SVG width */
    margin: auto; /* Center the word cloud */
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #f9f9f9; /* Light background for visibility */
  }
  </style>
  


