<template>
  <div>
    <v-row align="center" justify="center" class="mt-1 mb-0">
      <h3>Profit View of Company: {{ $props.selectedCompanyName }}</h3>
    </v-row>
    <div style="height: 90vh">
      <div id='myLinePlot' style="height: inherit"></div>
    </div>
  </div>
</template>


<script>
import Plotly from 'plotly.js/dist/plotly';
export default {
  name: "LinePlot",
  props: ["selectedCompanyName", "selectedCompany", "selectedAlgorithm"],
  data: () => ({
    LinePlotData: {x: [], y: []}
  }),
  mounted() {
    this.fetchData()
  },
  watch: {
    selectedCompany() {
      console.log("Watch in Lineplot for selectedCompany triggered ");
      this.LinePlotData.x = [];
      this.LinePlotData.y = [];

      this.fetchData();
    },
    selectedAlgorithm() {
      this.LinePlotData.x = [];
      this.LinePlotData.y = [];

      this.fetchData();
    }
  },
  methods: {
    async fetchData() {
      // req URL to retrieve single company from backend
      const reqUrl = `http://127.0.0.1:5000/companies/${this.selectedCompany}?algorithm=${this.selectedAlgorithm}`;
      console.log("LinePlot ReqURL:", reqUrl);

      // await response and data
      const response = await fetch(reqUrl)
      const responseData = await response.json();
      console.log("responseData in LinePlotcode", responseData);


      // Clear previous data
      this.LinePlotData.x = [];
      this.LinePlotData.y = [];
      this.LinePlotData.predictedY = []; // Ensure this array is initialized

      // Transform data to usable by line plot
      if (Array.isArray(responseData.profit)) {
        responseData.profit.forEach((profit) => {
          this.LinePlotData.x.push(profit.year);
          this.LinePlotData.y.push(profit.value);
        });
      } else {
        console.warn("Profit data is not an array:", responseData.profit);
      }

      // Check if the selected algorithm is for predictions
      if (this.$props.selectedAlgorithm === 'random' || this.$props.selectedAlgorithm === 'regression') {
        // Add the predicted year (2022)
        this.LinePlotData.x.push(2022);
        // Add the corresponding predicted value (this example assumes it's the last known value)
        this.LinePlotData.predictedY.push(responseData.profit[0].value); // Adjust as needed for the actual predicted value
      }

      // draw the lineplot after the data is transformed
      this.drawLinePlot()
    },
    drawLinePlot() {
      // Filter for the real values (up to 2021)
      var trace1 = {
        x: this.LinePlotData.x.filter(year => year <= 2021),  // Ensure x is up to 2021
        y: this.LinePlotData.y.filter((_, idx) => this.LinePlotData.x[idx] <= 2021), // Match the y values up to 2021
        type: 'scatter',
        mode: 'lines+markers', // Add markers for real values
        name: 'Real Values',
        line: { color: '#1E90FF' } // Blue line for real values
      };

      // Find the value for the year 2021
      const lastRealValue = this.LinePlotData.y.find((val, idx) => this.LinePlotData.x[idx] === 2021);
      // Find the value for the year 2022 (predicted value)
      const predictedValue = this.LinePlotData.y.find((val, idx) => this.LinePlotData.x[idx] === 2022);

      // Predicted trace from 2021 to 2022
      var trace2 = {
        x: [2021, 2022], // The x values are just 2021 and 2022
        y: [lastRealValue, predictedValue], // Start from the 2021 value and go to the predicted 2022 value
        type: 'scatter',
        mode: 'lines', // A dashed line for predicted values
        name: 'Predicted Values',
        line: { color: '#FF6347', dash: 'dash' } // Orange dashed line for predicted values
      };

      const uniqueYears = [...new Set(this.LinePlotData.x)];

      var data = [trace1];
      if (this.$props.selectedAlgorithm === 'random' || this.$props.selectedAlgorithm === 'regression') {
        data.push(trace2); // Add predicted trace only for prediction algorithms
      }

      var layout = {
        xaxis: {
          title: "Year",
          tickvals: uniqueYears, // Set the tick values to unique years
          ticktext: uniqueYears.map(year => year.toString()), // Ensure the ticks are displayed as strings
        },
        yaxis: { title: "Profit" }
      };

      var config = { responsive: true, displayModeBar: false };
      Plotly.newPlot('myLinePlot', data, layout, config);
    }
  }
}
</script>


