<template>
    <div>
        <ConfigurationPanel @year-changed="onYearChanged" />

        
      <!-- Main Content Section -->
      <v-container fluid class="full-height">
        <v-row class="full-height">
          <!-- Column 1 -->
          <v-col cols="12" md="4" class="full-height">
            <!-- Row 1, Widget 1 -->
            <v-card class="widget mb-4">
              <div class="control-panel-font">Dominating Countries</div>
              <MostDominatingCountries :selectedYear="selectedYear" />
            </v-card>
            <!-- Row 2, Widget 2 -->
            <v-card class="widget">
              <div class="control-panel-font">Widget 2 Title</div>
              <div class="widget-placeholder">Placeholder for Widget 2</div>
            </v-card>
          </v-col>
  
          <!-- Column 2 -->
          <v-col cols="12" md="4" class="full-height">
            <!-- Row 1, Widget 3 -->
            <v-card class="widget mb-4">
              <div class="control-panel-font">Widget 3 Title</div>
              <div class="widget-placeholder">Placeholder for Widget 3</div>
            </v-card>
            <!-- Row 2, Widget 4 -->
            <v-card class="widget">
              <div class="control-panel-font">Widget 4 Title</div>
              <div class="widget-placeholder">Placeholder for Widget 4</div>
            </v-card>
          </v-col>
  
          <!-- Column 3 (spans two rows) -->
          <v-col cols="12" md="4" class="full-height">
            <v-card class="widget h-100">
              <div class="control-panel-font">Widget 5 Title</div>
              <div class="widget-placeholder h-100">Placeholder for Widget 5</div>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </div>
  </template>

<script>
import ConfigurationPanel from './ConfigurationPanel.vue';
import MostDominatingCountries from './MostDominatingCountries.vue';

export default {
  components: { ConfigurationPanel, MostDominatingCountries },
  data() {
    return {
      selectedYear: null, // The currently selected year
    };
  },
  methods: {
    onYearChanged(year) {
      this.selectedYear = year; // Update the selected year
    },
  },
};
</script>
  
  <style scoped>

  /* Ensures the container takes up the full viewport height */
  .full-height {
    height: calc(100vh - 90px); /* Subtract header height */
  }
  
  /* Widgets should fill their respective rows and columns */
  .widget {
    height: calc(50% - 16px); /* Divides column into two rows with spacing */
  }
  
  /* Space between widgets in columns */
  .mb-4 {
    margin-bottom: 16px;
  }
  
  /* Styling for widget titles */
  .control-panel-font {
    font-family: "Open Sans", verdana, arial, sans-serif;
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 10px;
  }
  
  /* Placeholder styling for visual representation */
  .widget-placeholder {
    background-color: #f0f0f0;
    border: 1px dashed #ccc;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #888;
    height: 100%;
  }
  </style>
  