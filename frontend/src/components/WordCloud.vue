<template>
    <div>
      <v-card>
        <div id="word-cloud" class="word-cloud-container"></div>
      </v-card>
    </div>
  </template>
  
  <script>
  import * as d3 from "d3";
  import cloud from "d3-cloud";
  import axios from "axios";
  
  export default {
    props: ["selectedYear"], // Accept the selected year as a prop
    data() {
      return {
        wordCloudData: [], // Data for the word cloud
      };
    },
    watch: {
      selectedYear: {
        immediate: true, // Fetch word cloud data when the component is mounted
        handler(newYear) {
          this.fetchWordCloudData(newYear);
        },
      },
    },
    mounted() {
        this.fetchWordCloudData(this.selectedYear);
    },
    methods: {
      async fetchWordCloudData(year) {
        try {
          const response = await axios.get("http://127.0.0.1:5000/api/word_cloud", {
            params: { year },
          });
          this.wordCloudData = response.data; // Store the word cloud data
          this.renderWordCloud(); // Render the word cloud
        } catch (error) {
          console.error("Error fetching word cloud data:", error);
        }
      },
      renderWordCloud() {
        const width = 400;
        const height = 300;
  
        // Clear the previous word cloud
        d3.select("#word-cloud").selectAll("*").remove();
  
        const layout = cloud()
          .size([width, height])
          .words(
            this.wordCloudData.map((d) => ({
              text: d.word,
              size: d.count * 10, // Scale size by frequency
            }))
          )
          .padding(5)
          .rotate(() => ~~(Math.random() * 2) * 90) // Randomly rotate words
          .font("Impact")
          .fontSize((d) => d.size)
          .on("end", this.draw);
  
        layout.start();
      },
      draw(words) {
        const width = 400;
        const height = 300;
  
        d3.select("#word-cloud")
          .append("svg")
          .attr("width", width)
          .attr("height", height)
          .append("g")
          .attr("transform", `translate(${width / 2},${height / 2})`)
          .selectAll("text")
          .data(words)
          .enter()
          .append("text")
          .style("font-size", (d) => `${d.size}px`)
          .style("font-family", "Impact")
          .style("fill", () => d3.schemeCategory10[Math.floor(Math.random() * 10)]) // Random colors
          .attr("text-anchor", "middle")
          .attr("transform", (d) => `translate(${d.x},${d.y})rotate(${d.rotate})`)
          .text((d) => d.text);
      },
    },
  };
  </script>
  
  <style scoped>
  .word-cloud-container {
    width: 100%;
    height: 400px;
  }
  </style>
  