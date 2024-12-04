<template>
  <div>
    <v-container fluid class="header">
      <v-row align="center" justify="space-between" class="full-height">
        <!-- Country Selector (Left) -->
        <v-col cols="3" class="selectors-section">
          <v-card-text>
            <div v-if="currentPage === 'Performance'">
              <!-- Show Performance specific configuration -->
              <v-row class="country-selector">
                <v-col cols="12">
                  <v-select
                    :items="availableCountries"
                    v-model="selectedCountriesInternal"
                    label="Select Countries"
                    dense
                    outlined
                    multiple
                    class="custom-dropdown"
                    style="width: 100%;" 
                    @change="(val) => { console.log('Selected:', val); emitSelectedCountries() }"
                  >
                  </v-select>
                </v-col>
              </v-row>
            </div>
          </v-card-text>
        </v-col>
        
        <!-- Vertical Divider -->
        <v-col cols="1" class="divider-section full-height">
          <div class="vertical-divider"></div>
        </v-col>

        <!-- Empty Spacer for Center Alignment -->
        <v-col cols="1"></v-col>

        <!-- Year Range Slider (Right) -->
        <v-col cols="7" class="slider-section">
          <div id="year-range-container" class="slider-container">
            <p id="yearRangeLabel" class="slider-label">
              Year Range: {{ selectedYearRange[0] }} - {{ selectedYearRange[1] }}
            </p>
            <div id="year-range-slider" class="slider"></div>
            <div class="slider-year-labels">
              <span class="slider-start-year">1957</span>
              <span class="slider-end-year">2022</span>
            </div>
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
  
  props: ["currentPage", "selectedCountries"], // Receive currentPage as a prop from MainContainer

  data() {
    return {
      years: [], // Populate dynamically from backend
      selectedYear: null, // The currently selected year
      selectedYearRange: [null, null], // Year range from the slider
      availableCountries: ["Sweden", "Norway", "Germany", "France", "Italy"],
      selectedCountriesInternal: ["Sweden", "Norway"],
    };
  },
  mounted() {
    this.fetchAvailableYears();

  },

  watch: {
    // Sync the internal state with the prop when it changes
    selectedCountries: {
      immediate: true,
      handler(newVal) {
        this.selectedCountriesInternal = newVal;
      },
    },

    selectedCountriesInternal: {
      deep: true,
      handler(newVal) {
        console.log("Watcher triggered: Selected countries updated:", newVal);
        this.emitSelectedCountries();
      },
    },
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

    emitSelectedCountries() {
      // Emit the selected countries to MainContainer.vue
      console.log("Emitting selected countries from ConfigPanel to MainContainer:", this.selectedCountriesInternal);
      this.$emit("update-selected-countries", this.selectedCountriesInternal);
    },


  },
};
</script>

<style>

.noUi-connect {
  background: #09529c; /* Dodger Blue for the selected range */
}

/* Customize the handles (circles on the sides) */
.noUi-handle {
  background: #222222; /* Match the dark theme */
  border: 1px groove #5a5ac6; /* Add a highlight effect */
}

/* Slider track (unselected area) */
.noUi-base {
  background: #888888; /* Match your UI */
}

/* Slider handles on hover */
.noUi-handle:hover {
  border-color: #aaaaff; /* Slightly brighter for hover effect */
}

/* Active handle during dragging */
.noUi-handle.noUi-active {
  border-color: #ffffff; /* Highlight active handle */
}

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
  padding-left: 10px;
}

.full-height {
  height: 100%;
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
  margin-bottom: 10px; /* Space between label and slider */
  font-weight: bold;
  font-size: 16px; /* Adjust font size for better readability */
  text-align: right;
  color: white; /* Match the dark theme */
}

.slider {
  width: 70%; /* Adjust width as needed */
  margin: 10px 0; /* Add spacing between slider and labels */
}

.slider-section {
  margin-left:auto;
  text-align: right;
}

.slider-year-labels {
  width: 50%; /* Match the slider width */
  display: flex;
  justify-content: space-between;
  font-size: 14px; /* Adjust font size for labels */
  position: relative;
  margin-top: 0px; /* Add more space below the slider */
}

.slider-start-year,
.slider-end-year {
  font-weight: bold;
  color: white; /* Ensure labels match the dark theme */
  transform: translateY(5px); /* Move the labels slightly downward */
  font-size: 14px; /* Keep the labels legible */
}


.country-selector {
  display: flex;
  justify-content: space-between;
  padding: 0 20px;
}


.header-title {
  font-family: "Open Sans", verdana, arial, sans-serif;
  font-size: 24px;
  font-weight: bold;
  margin: 0;
}

.dropdown {
  width: 200px;
}

.vertical-divider {
  border-left: 2px solid #444; /* Match the navbar divider */
  height: 100%; /* Ensure it spans the height of its container */
  margin: auto; /* Center it vertically */
  opacity: 0.8; /* Slight transparency for a subtle effect */
}


</style>

