<template>
  <div class="main-container">
    <v-card>
      <v-card-title class="controls-container">
        <!-- Dropdown for selecting number of clusters -->
        <v-select
          :items="[3, 4, 5, 6, 7 ,8]"
          label="Number of Clusters"
          v-model="numberOfClusters"
          outlined
          dense
          class="dropdown"
        />
        <v-switch
          label="Regional Data"
          v-model="regionalData"
          outlined
          dense
        />
      </v-card-title>
      <div class="content-container">

        <div class="plot-container">
          <div id="scatterplot" class="scatterplot"></div>
        </div>

        <div class="widget-container">
          <div id="barchart-container"></div>
        </div>

      </div>
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
      explainedVariance: [], // Holds PCA explained variance
      numberOfClusters: 5, // Default number of clusters
      regionalData: false,
      regionColorMap: {
          "Southern Europe": "#17becf",  // Teal
          "Western Europe": "#bcbd22",         // Yellow-green
          "Eastern Europe": "#8c564b",           // Brown
          "Northern Europe": "#e377c2",         // Pink
          "Non-European": "#7f7f7f",        // Gray
          // "Southern Europe": "#d62728",  // Red
          // "Western Europe": "#2ca02c",         // Green
          // "Eastern Europe": "#1f77b4",           // Blue
          // "Northern Europe": "#9467bd",         // Purple
          // "Non-European": "#ff7f0e",        // Magenta
        },
      clusterColorMap: d3.schemeCategory10,
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
    regionalData: {
      immediate: true, // React immediately when the toggle changes
      handler() {
        this.drawScatterPlot(); // Redraw the plot with the updated color scheme
        this.drawBarChart(); // Redraw the plot with the updated color scheme
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
        this.clusterData = response.data.clusters; // Cluster data
        this.explainedVariance = response.data.explained_variance; // Explained variance
        this.drawScatterPlot(); // Render the visualization
        this.drawBarChart();
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

      // Define scales (still used for positioning circles)
      const xScale = d3.scaleLinear()
          .domain(d3.extent(this.clusterData, (d) => d.x))
          .range([50, width - 50]); // Add padding
      const yScale = d3.scaleLinear()
          .domain(d3.extent(this.clusterData, (d) => d.y))
          .range([height - 50, 50]); // Invert y-axis for correct orientation

      // Create tooltip
      const tooltip = d3.select("body")
        .append("div")
        .attr("class", "tooltip")
        .style("position", "absolute")
        .style("background", "white")
        .style("border", "1px solid #ccc")
        .style("padding", "12px")
        .style("box-shadow", "0 2px 4px rgba(0,0,0,0.2)")
        .style("pointer-events", "none")
        .style("visibility", "hidden");

      console.log("this.explainedVariance:", this.explainedVariance);

      // Add X-axis label (no ticks)
      svg.append("text")
          .attr("x", width / 2)
          .attr("y", height - 10) // Position below the chart
          .attr("text-anchor", "middle")
          .attr("font-size", "16px")
          .attr("fill", "black")
          .text(`PC1 (${this.explainedVariance[0] ? this.explainedVariance[0].toFixed(1) : "N/A"}% variance)`);

      // Add Y-axis label (no ticks)
      svg.append("text")
          .attr("transform", "rotate(-90)") // Rotate for Y-axis
          .attr("x", -height / 2)
          .attr("y", 20) // Position to the left of the chart
          .attr("text-anchor", "middle")
          .attr("font-size", "16px")
          .attr("fill", "black")
          .text(`PC2 (${this.explainedVariance[1] ? this.explainedVariance[1].toFixed(1) : "N/A"}% variance)`);

      // Add circles for each data point
      svg.selectAll("circle")
          .data(this.clusterData)
          .enter()
          .append("circle")
          .attr("cx", (d) => xScale(d.x))
          .attr("cy", (d) => yScale(d.y))
          .attr("r", 12) // Circle size
          .attr("fill", (d) => {
            if (this.regionalData) {
              return this.regionColorMap[d.region];// Use region-based colors
            } else {
              return  d3.schemeCategory10[d.cluster % 10]; // Cluster-based color
            }
          })
          .attr("opacity", 0.8)
          .on("mouseover", (event, d) => {
            tooltip
              .style("visibility", "visible")
              .html(`<strong>${d.country_name}</strong>`); // Show country_name
          })
          .on("mousemove", (event) => {
            tooltip
              .style("top", `${event.pageY + 10}px`) // Position below mouse
              .style("left", `${event.pageX + 10}px`); // Position to the right of mouse
          })
          .on("mouseout", () => {
            tooltip.style("visibility", "hidden"); // Hide tooltip
          })
          .attr("data-country", (d) => d.country_name);

      // Add country labels
      svg.selectAll("text.country-label")
          .data(this.clusterData)
          .enter()
          .append("text")
          .attr("class", "country-label")
          .attr("x", (d) => xScale(d.x) + 12) // Offset from circle
          .attr("y", (d) => yScale(d.y))
          .attr("font-size", "20px")
          .attr("fill", "black")
          .text((d) => d.country);
    },

    drawBarChart(){
      const margin = { top: 20, right: 20, bottom: 40, left: 120 };
      const width = 300;
      const height = 150;
      d3.select("#barchart-container").selectAll("*").remove();
      const tooltip = d3.select("body")
        .append("div")
        .attr("class", "tooltip")
        .style("position", "absolute")
        .style("background", "white")
        .style("border", "1px solid #ccc")
        .style("padding", "8px")
        .style("box-shadow", "0 2px 4px rgba(0,0,0,0.2)")
        .style("pointer-events", "none")
        .style("visibility", "hidden");
      // Group the data by cluster and count occurrences of each region
      const clusterRegionCounts = this.clusterData.reduce((acc, item) => {
        if (!acc[item.cluster]) acc[item.cluster] = {};
        if (!acc[item.cluster][item.region]) {
          acc[item.cluster][item.region] = { count: 0, countries: [] }; // Initialize as object
        }
        acc[item.cluster][item.region].count++;
        acc[item.cluster][item.region].countries.push(item.country_name);
        return acc;
      }, {});
      let globalMax = 0;
      Object.values(clusterRegionCounts).forEach(cluster => {
        const counts = Object.values(cluster).map(region => region.count);
        const maxInCluster = Math.max(...counts);
        globalMax = Math.max(globalMax, maxInCluster);
      });
            
      const allRegions = Object.keys(this.regionColorMap);
      Object.keys(clusterRegionCounts).forEach((clusterId) => {
        const clusterData = clusterRegionCounts[clusterId];
        // Ensure that all regions are included, even if their count is zero
        const regionNames = allRegions;
        const counts = regionNames.map(region => clusterData[region]?.count || 0); // 0 if region has no data        
        const countryLists = regionNames.map((region) => clusterData[region]?.countries || []);
        const svg = d3.select("#barchart-container")
          .append("svg")
          .attr("width", width + margin.left + margin.right)
          .attr("height", height + margin.top + margin.bottom)
          .append("g")
          .attr("transform", `translate(${margin.left},${margin.top})`);
        // Create the x and y scales
        const xScale = d3.scaleLinear()
          .domain([0, globalMax])
          .range([0, width])
          .nice();
        const yScale = d3.scaleBand()
          .domain(regionNames)
          .range([0, height])
          .padding(0.1);
        const clusterColor = this.clusterColorMap[clusterId % this.clusterColorMap.length];
        // Create bars for each region
        svg.selectAll(".bar")
          .data(counts.map((d, i) => ({ value: d, index: i })))
          .enter()
          .append("rect")
          .attr("class", "bar")
          .attr("x", 0)
          .attr("y", (d) => yScale(regionNames[d.index]))
          .attr("height", yScale.bandwidth())
          .attr("width", (d) => xScale(d.value))
          // .attr("fill", "#7f7f7f");
          // .attr("fill", (d) => this.regionColorMap[regionNames[d.index]])
          .attr("fill", (d) => {
            return this.regionalData
              ? this.regionColorMap[regionNames[d.index]] // Use region-based colors
              : clusterColor; // Cluster-based color
          })
          .on("mouseover", (event, d) => {
              const countries = countryLists[d.index] || [];
              const countriesText = countries.length > 0 ? countries.join(", ") : "No countries available";
              tooltip.style("visibility", "visible").html(`
                <strong>Region:</strong> ${regionNames[d.index]}<br>
                <strong>Count:</strong> ${d.value}<br>
                <strong>Countries:</strong><br>${countriesText}
              `);
              d3.selectAll("#scatterplot circle")
                .attr("opacity", (node) => (countries.includes(node.country_name) ? 1 : 0.2));
            
          })
          .on("mousemove", (event) => {
            tooltip
              .style("top", `${event.pageY + 10}px`)
              .style("left", `${event.pageX + 10}px`);
          })
          .on("mouseout", () => {
            tooltip.style("visibility", "hidden");
            d3.selectAll("#scatterplot circle").attr("opacity", 0.8);
          });
            // Add y-axis
        svg.append("g")
          .attr("class", "y-axis")
          .call(d3.axisLeft(yScale))
          .selectAll("text")
          .style("font-size", "13px");
        // Add x-axis
        svg.append("g")
          .attr("class", "x-axis")
          .attr("transform", `translate(0,${height})`)
          .call(d3.axisBottom(xScale).ticks(globalMax).tickFormat(d3.format("d")))
          .selectAll("text")
          .style("font-size", "13px");
        // Add a title for each cluster's chart
        svg.append("text")
          .attr("x", width / 2)
          .attr("y", -10)
          .attr("text-anchor", "middle")
          .attr("font-size", "15px")
          .attr("font-weight", "bold")
          .attr("fill", clusterColor)
          .text(`Cluster ${parseInt(clusterId) + 1}`);
      });
    }
  },
};
</script>

<style scoped>
.main-container {
  display: flex;
  flex-direction: column;
}

.controls-container {
  display: left;
  flex-wrap: wrap;
  align-items: center; /* Ensures all controls align vertically */
  margin-bottom: 10px;
}

.content-container {
  display: flex;
  align-items: flex-start; /* Align all child containers to the top */
}

.plot-container {
  flex: 2;
}

.widget-container {
  display: flex;
  flex-direction: column; /* Stacks bar charts vertically */
  flex: 1;
  margin-left: 20px;
  padding: 10px;
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 8px;
  align-self: flex-start;
  position: relative; /* Ensures the container is positioned correctly */
  overflow-y: auto; /* Allows scrolling if the content exceeds the container's height */
  max-height: 800px; /* Adjust to your preferred height */
}

#barchart-container::-webkit-scrollbar {
  width: 8px;
}

#barchart-container::-webkit-scrollbar-thumb {
  background-color: #ccc;
  border-radius: 4px;
}

#barchart-container::-webkit-scrollbar-thumb:hover {
  background-color: #aaa;
}

</style>