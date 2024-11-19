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
          
            <!-- Year Range Slider -->
            <div id="year-range-container" class="slider-container">
              <!-- Year Range Label -->
              <p id="yearRangeLabel" class="slider-label">
                Year Range: {{ selectedYearRange[0] }} - {{ selectedYearRange[1] }}
              </p>

              <!-- Slider -->
              <div id="year-range-slider" class="slider"></div>

              <!-- Slider Year Labels -->
              <div class="slider-year-labels">
                <span class="slider-start-year">1957</span>
                <span class="slider-end-year">2022</span>
              </div>
            </div>


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
import noUiSlider from "nouislider";
import 'nouislider/dist/nouislider.css';

export default {
  data() {
    return {
      years: [], // Populate dynamically from backend
      selectedYear: null, // The currently selected year
      selectedYearRange: [null, null], // Year range from the slider
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
          this.selectedYear = this.years[0]; // Default to the first available year
          this.initializeYearRangeSlider(this.years[this.years.length-1], this.years[0]);
        }
      } catch (error) {
        console.error("Error fetching available years:", error);
      }
    },
    initializeYearRangeSlider(minYear, maxYear) {
      const slider = document.getElementById("year-range-slider");
      

      noUiSlider.create(slider, {
        start: [minYear, maxYear],
        connect: true,
        range: {
          min: minYear,
          max: maxYear,
        },
        step: 1,
      });

      // Update the year range label and emit changes
      slider.noUiSlider.on("update", (values) => {
        this.onYearRangeChange(values.map((v) => Math.round(v)));
      });
    },
    onYearChange(newValue) {
      this.selectedYear = newValue; // Update selectedYear with the new value
      console.log("Year changed to:", this.selectedYear); // Debugging log
      this.$emit("yearChanged", this.selectedYear); // Emit event to parent
    },

    onYearRangeChange(newRange) {
      this.selectedYearRange = newRange; // Update selectedYearRange with the new range
      // console.log("Year range changed to:", this.selectedYearRange); // Debugging log
      this.$emit("yearRangeChanged", this.selectedYearRange); // Emit event to parent
    },

  },
};
</script>

<style scoped>
/* Header Section */
.header {
  padding: 16px;
  border-bottom: 1px solid #ddd;
  width: 100%;
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
  flex-wrap: wrap;
  gap: 16px;
  justify-content: space-between;
}

.selector {
  width: 30%;
}

.slider-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.slider-label {
  margin-bottom: 10px; /* Add space between label and slider */
  font-weight: bold;
  font-size: 16px;
  text-align: center;
}

.slider {
  width: 90%; /* Adjust width as needed */
  margin: 10px 0; /* Add spacing between slider and year labels */
}

.slider-year-labels {
  width: 90%; /* Match the slider width */
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  position: relative;
  margin-top: -10px; /* Adjust position to align with slider */
}

.slider-start-year,
.slider-end-year {
  font-weight: bold;
}


.header-title {
  font-family: "Open Sans", verdana, arial, sans-serif;
  font-size: 24px;
  font-weight: bold;
  margin: 0;
}
</style>

