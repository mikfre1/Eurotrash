<template>
  <div>
    <v-card>
      <!-- World Map -->
      <div id="worldmap" class="world-map"></div>
    </v-card>
  </div>
</template>

<script>
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import axios from "axios";

export default {
  props: ["selectedYearRange"],
  data: () => ({
    countryData: [], // Data for country dominance
    map: null, // Leaflet map instance
    geoJsonLayer: null, // Layer for GeoJSON countries
  }),
  watch: {
    selectedYearRange: {
      immediate: true, // Fetch data on initial load
      handler() {
        this.fetchCountryData(); // Fetch new data
      },
    },
    countryData(newData) {
    if (this.geoJsonLayer) {
      this.geoJsonLayer.eachLayer((layer) => {
        const feature = layer.feature;
        const country = newData.find(
          (c) => c.to_country.trim().toLowerCase() === feature.properties.name.trim().toLowerCase()
        );
        const count = country ? country.total_points : "No data available";
        layer.bindPopup(
          `<strong>${feature.properties.name}</strong><br>Total Points: ${count}`
        );
      });
    }
  }
  },
  mounted() {
    this.$nextTick(() => {
      this.initializeMap();
    });
    this.fetchCountryData();
  },
  methods: {
    async fetchCountryData() {
      try {
        const response = await axios.get("http://127.0.0.1:5000/api/most_dominating_countries", {
          params: { 
            yearRangeStart: this.selectedYearRange[0],
            yearRangeEnd: this.selectedYearRange[1]
          },
        });
        this.countryData = response.data;
      

        this.updateMap(); // Update map with new data
      } catch (error) {
        console.error("Error fetching country data:", error);
      }
    },
    async initializeMap() {
      this.map = L.map("worldmap").setView([20, 0], 2);
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      }).addTo(this.map);

      // Fetch the GeoJSON file dynamically from the public folder
      const response = await fetch("/world.geojson");
      const geojson = await response.json();

      // Add GeoJSON layer to the map
      this.geoJsonLayer = L.geoJson(geojson, {
        style: this.styleCountry,
        onEachFeature: this.onEachFeature,
      }).addTo(this.map);
    },
    updateMap() {
      if (this.geoJsonLayer) {
        this.geoJsonLayer.setStyle(this.styleCountry); // Apply styles
      }
    },
    styleCountry(feature) {
      // Find the country in the data
      const country = this.countryData.find(
        (c) => c.to_country === feature.properties.name
      );
      const totalPoints = country ? country.total_points : 0;

      // Determine color based on the distribution of total_points
      const getColor = (value, thresholds) => {
        return value > thresholds[4]
          ? "#FF0000" // Bright red for the top tier
          : value > thresholds[3]
          ? "#FF4500" // Orange-red
          : value > thresholds[2]
          ? "#FFA500" // Orange
          : value > thresholds[1]
          ? "#FFFF00" // Yellow
          : value > thresholds[0]
          ? "#00FF00" // Bright green
          : "#D3D3D3"; // Light gray for no data
      };

      // Calculate distribution thresholds dynamically
      const values = this.countryData.map((c) => c.total_points);
      const thresholds = this.calculateQuantiles(values);

      return {
        fillColor: getColor(totalPoints, thresholds),
        weight: 1,
        opacity: 1,
        color: "gray",
        fillOpacity: 0.9, // Make the colors more opaque
      };
    },
    calculateQuantiles(values) {
      if (!values || values.length === 0) {
        return [0, 0, 0, 0, 0]; // Default thresholds
      }

      // Sort values
      const sortedValues = values.sort((a, b) => a - b);

      // Calculate quantiles (e.g., 10%, 30%, 50%, 70%, 90%)
      const quantiles = [0.1, 0.3, 0.5, 0.7, 0.9].map((q) => {
        const pos = Math.floor(q * sortedValues.length) - 1;
        return sortedValues[Math.max(pos, 0)];
      });
      
      return quantiles;
    },
    onEachFeature(feature, layer) {
      // Add a popup for each country
      console.log(feature.properties.name)
      const country = this.countryData.find(
        (c) => c.to_country === feature.properties.name
      );
      const count = country ? country.total_points : "undefined";
      layer.bindPopup(
        `<strong>${feature.properties.name}</strong><br>Total Points: ${count}`
      );
    },
  },
};
</script>

<style scoped>
.world-map {
  height: 800px;
  width: 100%;
}
</style>