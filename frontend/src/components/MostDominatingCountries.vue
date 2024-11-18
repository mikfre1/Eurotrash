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
  props: ["selectedYear"],
  data: () => ({
    countryData: [], // Data for country dominance
    map: null, // Leaflet map instance
    geoJsonLayer: null, // Layer for GeoJSON countries
  }),
  watch: {
    selectedYear: {
      immediate: true, // Fetch data on initial load
      handler(newYear) {
        console.log("Year changed to:", newYear); // Debugging log
        this.fetchCountryData(newYear); // Fetch new data
      },
    },
  },
  mounted() {
    this.initializeMap();
    this.fetchCountryData(this.selectedYear);
  },
  methods: {
    async fetchCountryData() {
      try {
        const response = await axios.get("http://127.0.0.1:5000/api/most_dominating_countries", {
          params: { year: this.selectedYear },
        });
        this.countryData = response.data;
        console.log("Fetched data for year:", this.selectedYear, this.countryData); // Debugging log
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
        this.geoJsonLayer.eachLayer((layer) => {
          // Reapply styles
          const feature = layer.feature;
          layer.setStyle(this.styleCountry(feature));

          // Update popup content
          this.onEachFeature(feature, layer);
        });
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

    // Calculate quantiles (e.g., 20%, 40%, 60%, 80%, 100%)
    const quantiles = [0.2, 0.4, 0.6, 0.8, 1.0].map((q) => {
      const pos = Math.floor(q * sortedValues.length) - 1;
      return sortedValues[Math.max(pos, 0)];
    });

    // console.log("Calculated quantiles:", quantiles); // Debugging log
    return quantiles;
  },
    onEachFeature(feature, layer) {
      // Add a popup for each country
      const country = this.countryData.find(
        (c) => c.to_country === feature.properties.name
      );
      const count = country ? country.total_points : 0;
      layer.bindPopup(
        `<strong>${feature.properties.name}</strong><br>Total Points: ${count}`
      );
    },
  },
};
</script>

<style scoped>
.world-map {
  height: 400px;
  width: 100%;
}
</style>
