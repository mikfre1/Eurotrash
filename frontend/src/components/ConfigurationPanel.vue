<template>
  <div>
    <v-container fluid class="header">
      <v-row align="center" justify="space-between">
        <!-- Title Section -->
        <v-col cols="12" md="6" class="title-section">
          <h1 class="header-title">Eurotrash at a Glance</h1>
        </v-col>

        <!-- Selectors Section -->
        <v-col cols="12" md="6" class="selectors-section">
          <div class="selectors">
            <!-- Year Selector -->
            <v-select
              :items="years"
              label="Select Year"
              dense
              outlined
              :model-value="selectedYear"
              @update:modelValue="onYearChange"
            />

            <!-- View Selector -->
            <v-select
              :items="views"
              label="View"
              dense
              outlined
              class="selector"
              v-model="selectedView"
            ></v-select>

            <!-- Country Selector -->
            <v-select
              :items="countries"
              label="Country"
              dense
              outlined
              class="selector"
              v-model="selectedCountry"
            ></v-select>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      years: [], // Populate dynamically from backend
      selectedYear: null, // The currently selected year
    };
  },
  mounted() {
    this.fetchAvailableYears();
  },
  methods: {
    async fetchAvailableYears() {
      try {
        const response = await axios.get("http://127.0.0.1:5000/api/available_years");
        this.years = response.data;

        if (this.years.length > 0) {
          this.selectedYear = this.years[0]; // Default to the most recent year
          console.log("Default year selected:", this.selectedYear); // Debugging log
          this.onYearChange(this.selectedYear); // Trigger map update for default year
        }
      } catch (error) {
        console.error("Error fetching available years:", error);
      }
    },
    onYearChange(newValue) {
      this.selectedYear = newValue; // Update selectedYear with the new value
      console.log("Year changed to:", this.selectedYear); // Debugging log
      this.$emit("yearChanged", this.selectedYear); // Emit event to parent
    },
  },
};

</script>

<style scoped>
/* Header Section */
.header {
  padding: 16px;
  border-bottom: 1px solid #ddd;
  width: 100%; /* Ensure the header spans the full width */
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}

/* Title Section */
.title-section {
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

/* Selectors Section */
.selectors-section {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

/* Selectors Styling */
.selectors {
  display: flex;
  width: 100%;
  justify-content: space-between; /* Ensures equal spacing between selectors */
}

.selector {
  width: 33.33%; /* Each selector takes up 33.33% of the selectors-section width */
}

/* Header Title Styling */
.header-title {
  font-family: "Open Sans", verdana, arial, sans-serif;
  font-size: 24px;
  font-weight: bold;
  margin: 0;
}
</style>
