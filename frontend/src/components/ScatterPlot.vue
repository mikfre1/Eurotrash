<template>
  <div>
    <v-row align="center" justify="center" class="mt-1 mb-0">
      <h3>Overview of {{ $props.selectedCategory }} Companies</h3>
    </v-row>
    <div style="height: 90vh">
      <div id='myScatterPlot' style="height: inherit"></div>
    </div>
  </div>
</template>

<script>
import Plotly from 'plotly.js/dist/plotly';

export default {
  name: "ScatterPlot",
  props: [
    "selectedCategory"
  ],
  data: () => ({
    ScatterPlotData: {x: [], y: [], name: [], colors: []},
    responseData: [] // Add this line
  }),
  mounted() {
    this.fetchData();
  },
  watch: {
    selectedCategory: function () {
      this.ScatterPlotData.x = [];
      this.ScatterPlotData.y = [];
      this.fetchData();
    }
  },
  methods: {
    async fetchData() {
      var reqUrl = 'http://127.0.0.1:5000/companies?category=' + this.$props.selectedCategory;
      console.log('ReqURL ' + reqUrl);
      const response = await fetch(reqUrl);
      this.responseData = await response.json(); // Store response data in this.responseData
      console.log("ResponseData from Scatterplot", this.responseData);

      // Clear previous data
      this.ScatterPlotData.name = [];
      this.ScatterPlotData.x = [];
      this.ScatterPlotData.y = [];
      this.ScatterPlotData.colors = [];

      const colorMap = {
        bank: '#0d457a',   // red
        tech: '#4CAF50',   // green
        health: '#00BFFF', // blue
      };

      // Transform data to be usable by scatterplot
      this.responseData.forEach((company) => {
        this.ScatterPlotData.name.push(company.name);
        this.ScatterPlotData.x.push(company.founding_year);
        this.ScatterPlotData.y.push(company.employees);
        this.ScatterPlotData.colors.push(colorMap[company.category] || colorMap.all); // Assign color based on category
      });
      // After the data is loaded, draw the plot
      this.drawScatterPlot();
    },
    drawScatterPlot() {
      var trace1 = {
        x: this.ScatterPlotData.x,
        y: this.ScatterPlotData.y,
        mode: 'markers',
        type: 'scatter',
        text: this.ScatterPlotData.name,
        marker: {
          color: this.ScatterPlotData.colors, // Use colors from data
          size: 12
        }
      };
      var data = [trace1];
      var layout = {
        xaxis: {title: "Founding Year"},
        yaxis: {title: "Number of Employees"},
      };
      var config = {responsive: true, displayModeBar: false};
      Plotly.newPlot('myScatterPlot', data, layout, config);
      this.clickScatterPlot();
    },
    clickScatterPlot() {
      var that = this;
      var myPlot = document.getElementById('myScatterPlot');
      myPlot.on('plotly_click', function (data) {
        for (var i = 0; i < data.points.length; i++) {
          let pn = data.points[i].pointNumber;
          let selectedCompanyId = pn + 1; // Assuming the IDs are sequential starting from 1

          // Emit the event to update the currently selected company
          that.$emit('changeCurrentlySelectedCompany', selectedCompanyId);

          // Find the category of the selected company from the fetched data
          const selectedCategory = that.responseData[pn].category; // Use this.responseData
          // Emit the category change to update the Configuration Panel
          that.$emit('changeSelectedCategory', selectedCategory);

          // Update the plot colors
          var colors = Array(that.ScatterPlotData.x.length).fill('#00000'); // Use the length of x data
          colors[pn] = '#3777ee'; // Change the selected point's color

          var update = {'marker': {color: colors, size: 12}};
          Plotly.restyle('myScatterPlot', update);
        }
      });
    }
  }
}
</script>
