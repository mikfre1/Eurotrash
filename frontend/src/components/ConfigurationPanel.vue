<template>
  <div>
    <v-container fluid class="header">
      <v-row align="center" justify="flex-start" class="full-height" style="gap: 20px; padding: 0 20px;">
        <!-- Country Selector (Shown only on Performance Page) -->
        <v-col cols="3" class="selectors-section" v-if="currentPage === 'Performance'">
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
          ></v-select>
        </v-col>

        <!-- Year Range Slider -->
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

.header {
  position: fixed;
  top: 0;
  z-index: 10;
  width: 100%;
  height: 95px; /* Allow dynamic height based on content */
  display: flex;
  align-items: center;
  background-color: var(--content-bg-color);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  padding: 0 20px;
}



/* Title Section */
.title-section {
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

/* Selectors Section */
.selectors-section {
  flex: 0 0 30%; /* Take 30% of the space */
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
  display: flex;
  flex-direction: column;
  align-items: center; /* Center the contents horizontally */
  width: 100%;
  padding-right: 30px; /* Add padding to the right edge */
}

.slider-label {
  margin-bottom: 10px;
  font-weight: bold;
  font-size: 16px;
  color: white;
  text-align: center; /* Center the text */
}

.slider {
  width: 100%; /* Allow the slider to take up full width */
}

.slider-section {
  flex: 1; /* Take the remaining space */
  padding-left: 10px;
}
.slider-year-labels {
  width: 100%; /* Match the slider width */
  display: flex;
  justify-content: space-between;
  font-size: 14px; /* Adjust font size for labels */
  position: relative;
  margin-top: 5px; /* Add more space below the slider */
}

.slider-start-year,
.slider-end-year {
  font-weight: bold;
  color: white; /* Ensure labels match the dark theme */
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

