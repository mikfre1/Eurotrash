<template>
  <div>
    <v-row align="center" justify="center" class="mt-1 mb-0">
      <h3> Employees of {{ $props.selectedCategory }} Companies</h3>
    </v-row>
    <div style="height: 90vh">
      <div id='myBarPlot' style="height: inherit"></div>
    </div>
  </div>
</template>

<script>
import Plotly from 'plotly.js/dist/plotly';

export default {
  name: "BarPlot",
  props: [
    "selectedCategory"
  ],
  data: () => ({
    BarPlotData: {x: [], y: [], name: [], avg: 0, colors: []},
    categoryColors: {
      tech: '#4CAF50',  // Tech companies color
      health: '#00BFFF', // Health companies color
      bank: '#0d457a',   // Bank companies color
      all: '#a9c3e8'     // Default color for 'All'
    }
  }),
  mounted() {
    this.fetchData();
  },
  watch: {
    selectedCategory: function () {
      this.BarPlotData.x = [];
      this.BarPlotData.y = [];
      this.BarPlotData.avg = 0;
      this.fetchData();
    }
  },
  methods: {
    async fetchData() {
      // req URL to retrieve companies from backend
      var reqUrl = 'http://127.0.0.1:5000/companies?category=' + this.$props.selectedCategory;
      console.log('ReqURL ' + reqUrl);

      // Await response and data
      const response = await fetch(reqUrl);
      const responseData = await response.json();
      console.log("ResponseData from MultiPlot", responseData);

      // Clear previous data
      this.BarPlotData.name = [];
      this.BarPlotData.x = [];
      this.BarPlotData.y = [];
      this.BarPlotData.colors = [];

      let totalEmployees = 0;

      // Assign colors based on the selected category
      let categoryColor = this.categoryColors[this.selectedCategory] || this.categoryColors.all;

      // Transform data to be usable by the bar plot
      responseData.forEach((company) => {
        this.BarPlotData.name.push(company.name);
        this.BarPlotData.x.push(company.name); // Companies for x-axis
        this.BarPlotData.y.push(company.employees); // Number of employees for y-axis
        this.BarPlotData.colors.push(categoryColor); // Assign the color based on the category
        totalEmployees += company.employees;
      });

      // Calculate the average number of employees
      this.BarPlotData.avg = totalEmployees / responseData.length;

      // After the data is loaded, draw the plot
      this.drawBarPlot();
    },

    drawBarPlot() {
      // Bar trace for companies
      var barTrace = {
        x: this.BarPlotData.x,
        y: this.BarPlotData.y,
        type: 'bar',
        text: this.BarPlotData.name,
        marker: {
          color: this.BarPlotData.colors // Use the colors array for the bars
        },
        name: 'Number of Employees'
      };

      // Line trace for average
      var avgLine = {
        x: this.BarPlotData.x,
        y: Array(this.BarPlotData.x.length).fill(this.BarPlotData.avg), // Same y value for all x points
        mode: 'lines',
        line: {
          color: 'black',
          dash: 'dash'
        },
        name: 'Average Employees of Category'
      };

      var data = [barTrace, avgLine];
      var layout = {
        xaxis: {title: "Companies"},
        yaxis: {title: "Number of Employees"},
      };
      var config = {responsive: true, displayModeBar: false};
      Plotly.newPlot('myBarPlot', data, layout, config);
    }
  }
}
</script>
