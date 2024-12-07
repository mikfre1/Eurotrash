
<template>
    <div>
      <v-card class="barchart-card">
        <div id="wordsbarchart" class="word-barchart-container"></div>
      </v-card>
    </div>
</template>
  
  <script>
  import axios from "axios";
  import * as d3 from "d3";
 
  
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
          this.fetchWordsBarChartData(); // Fetch data when the year range changes
        },
      },
      selectedFilter: {
        immediate: true, // React to filter changes
        handler() {
          this.fetchWordsBarChartData(); // Re-fetch data with the updated filter
        },
      },
    },
    methods: {
      async fetchWordsBarChartData() {
        try {
          console.log("Fetching word bar chart data for year:", this.selectedYearRange, "with filter:", this.selectedFilter);
          const response = await axios.get("http://127.0.0.1:5000/api/word_cloud_filter", {
            params: { 
              yearRangeStart: this.selectedYearRange[0],
              yearRangeEnd: this.selectedYearRange[1],
              filter: this.selectedFilter, // Pass the selected filter
            },
          });
          this.wordData = response.data;
          console.log("Words Bar Chart Data: ", this.wordData)

  
          if (this.wordData.length > 0) {
            this.renderBarChart(); // Render the word cloud if data exists
          } else {
            console.warn("No word data available for the selected year");
            d3.select("#wordcloud").html("<p>No data available</p>");
          }
        } catch (error) {
          console.error("Error fetching word cloud data:", error);
        }
      },


      async renderBarChart() {
        const margin = { top: 20, right: 20, bottom: 50, left: 50 };
        const containerWidth = document.getElementById("wordsbarchart").clientWidth;
        const containerHeight = 300; // Fixed height for better layout control

        const width = containerWidth - margin.left - margin.right;
        const height = containerHeight - margin.top - margin.bottom;

        // Clear previous chart
        
        d3.select("#wordsbarchart")
        .style("background-color", "#4b4b4b") // Ensure background color is applied
        .attr("class", "word-barchart-container") // Ensure the class is applied
        .selectAll("*") // Select all child elements
        .remove(); // Remove child elements

        // Append SVG element
        const svg = d3
            .select("#wordsbarchart")
            .append("svg")
            .attr("width", containerWidth)
            .attr("height", containerHeight)
            .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        // Scales
        const xScale = d3
            .scaleBand()
            .domain(this.wordData.map((d) => d.word))
            .range([0, width])
            .padding(0.2);

        const yScale = d3
            .scaleLinear()
            .domain([0, d3.max(this.wordData, (d) => d.count)])
            .range([height, 0]);

        // Axes
        const xAxis = d3.axisBottom(xScale);
        const yAxis = d3.axisLeft(yScale).ticks(5);

        // Draw X axis
        svg
            .append("g")
            .attr("class", "x-axis")
            .attr("transform", `translate(0, ${height})`)
            .call(xAxis)
            .selectAll("text")
            .attr("class", "axis-label")
            .attr("transform", "rotate(-45)")
            .style("text-anchor", "end");

        // Draw Y axis
        svg.append("g").attr("class", "y-axis").call(yAxis);

        // Bars
        svg
            .selectAll(".bar")
            .data(this.wordData)
            .join("rect")
            .attr("class", "bar")
            .attr("x", (d) => xScale(d.word))
            .attr("y", (d) => yScale(d.count))
            .attr("width", xScale.bandwidth())
            .attr("height", (d) => height - yScale(d.count))
            .attr("fill", "#17a2b8"); // Match theme color

        // Add grid lines
        svg
            .append("g")
            .attr("class", "y-grid")
            .call(
            d3
                .axisLeft(yScale)
                .tickSize(-width)
                .tickFormat("")
            )
            .selectAll(".domain")
            .remove();



      },
  
    },
  };
  </script>
  
<style scoped>


.barchart-card {
  background-color: transparent;
  padding: 20px;
  border-radius: 5px;
}

div#wordsbarchart.word-barchart-container {
  height: 300px;
  background-color: #4b4b4b !important;
  border-radius: 5px;

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

.y-grid line {
  stroke: #6c757d;
  stroke-opacity: 0.6;
}
</style>





