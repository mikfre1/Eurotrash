<template>
    <div>
      <div ref="heatmap" id="heatmap"></div>
    </div>
  </template>
  
  <script>
  import Plotly from "plotly.js-dist";
  import axios from "axios"; // Add axios for API calls
  
  export default {
    props: {
      selectedYearRange: {
        type: Number,
        required: true,
      },
    },
    data() {
      return {
        countries: [], // Holds the list of countries
        matrix: [], // Holds the voting matrix
      };
    },
    watch: {
      selectedYearRange: {
        immediate: true,
        handler() {
          this.fetchVotingData(); // Fetch data whenever the year changes
        },
      },
    },
    methods: {
      async fetchVotingData() {
        if (!this.selectedYearRange) {
          console.warn("Year is required to fetch voting data.");
          return;
        }
  
        try {
          const response = await axios.get("http://127.0.0.1:5000/api/countries_in_favor", {
            params: { 
              yearRangeStart: this.selectedYearRange[0],
              yearRangeEnd: this.selectedYearRange[1]
            },
          });
  
          const { countries, matrix } = response.data;
          if (countries && matrix) {
            this.countries = countries;
            this.matrix = matrix;
            this.renderHeatmap(); // Render the heatmap after data is fetched
          } else {
            console.warn("Invalid data received from the API.");
          }
        } catch (error) {
          console.error("Error fetching voting data:", error);
        }
      },
      renderHeatmap() {
  if (this.countries.length === 0 || this.matrix.length === 0) {
    console.warn("No data available to render heatmap.");
    return;
  }

  const zoomOutFactor = 0.0;

  // Calculate the default range for x and y axes
  const xRange = [-0.5, this.countries.length - 0.5];
  const yRange = [-0.5, this.countries.length - 0.5];

  // Adjust the range to zoom out by the specified factor
  const zoomedXRange = [
    xRange[0] - zoomOutFactor * (xRange[1] - xRange[0]),
    xRange[1] + zoomOutFactor * (xRange[1] - xRange[0]),
  ];
  const zoomedYRange = [
    yRange[0] - zoomOutFactor * (yRange[1] - yRange[0]),
    yRange[1] + zoomOutFactor * (yRange[1] - yRange[0]),
  ];

  // Define a custom colorscale with white as the base color
  const customColorscale = [
    [0, "white"],              // White for the lowest values (0 or missing)
    [0.1, "rgb(255,245,240)"], // Very light red
    [0.3, "rgb(254,224,210)"], // Light red
    [0.5, "rgb(252,187,161)"], // Moderate red
    [0.7, "rgb(252,146,114)"], // Slightly stronger red
    [0.85, "rgb(251,106,74)"], // Deeper red
    [1, "rgb(203,24,29)"],     // Very deep red for highest values
  ];

  // Find the minimum and maximum values in the matrix for scaling
  const zmin = 0;
  const zmax = Math.max(...this.matrix.flat());

  // Prepare data for Plotly
  const data = [
    {
      z: this.matrix,
      x: this.countries, // X-axis: countries that received votes
      y: this.countries, // Y-axis: countries that voted
      type: "heatmap",
      colorscale: customColorscale,
      hoverongaps: false,
      zmin: zmin, // Minimum value for the color range
      zmax: zmax, // Maximum value for the color range
    },
  ];

  const layout = {
    xaxis: {
      title: "To Country",
      tickangle: -45, // Rotate x-axis labels for better fit
      range: zoomedXRange, // Apply the zoomed-out range
    },
    yaxis: {
      title: "From Country",
      tickangle: -45,
      range: zoomedYRange, // Apply the zoomed-out range
    },
    margin: {
      t: 0, // Top margin
      l: 200, // Left margin
      r: 0, // Right margin
      b: 275, // Bottom margin (increased for x-axis labels)
    },
  };

  // Render the heatmap
  Plotly.newPlot(this.$refs.heatmap, data, layout, { responsive: true });
},
    },
  };
  </script>
  
  <style>
  #heatmap {
    width: 100%;
    height: 100%;
  }
  </style>
  