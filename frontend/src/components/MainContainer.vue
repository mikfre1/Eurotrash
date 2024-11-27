<template>
    <div>
        <ConfigurationPanel 
          @year-range-changed = "onYearRangeChanged"
        />
        <CountryCompositionDisclaimer/>


        
      <!-- Main Content Section -->
      <v-container fluid class="full-height">
  <v-row class="full-height">
    <!-- Column 1 -->
    <v-col cols="12" md="4" class="full-height">
      <!-- Row 1, Widget 1 -->
      <v-card class="widget mb-4">
        <div class="control-panel-font">Most Dominating Countries</div>
        <MostDominatingCountries :selectedYearRange="selectedYearRange" />
      </v-card>
      <!-- Row 2, Widget 2 -->
      <v-card class="widget">
        <div class="control-panel-font">Word Cloud</div>
        <WordCloud :selectedYearRange="selectedYearRange" />
      </v-card>
    </v-col>

    <!-- Column 2 -->
    <v-col cols="12" md="8" class="full-height">
      <!-- Row 1, Widget 3 -->
      <v-card class="widget mb-4">
        <div class="control-panel-font" style="margin-left: 20px;">Ranking Comparison</div>
        <RankingComparison :selectedYearRange="selectedYearRange" class="line-graph-container" />
      </v-card>
      <!-- Row 2, Widget 4 -->
      <v-card class="widget">
        <div class="control-panel-font">Voting Matrix</div>
        <VotingMatrix :selectedYearRange="selectedYearRange" :votingData="votingData" />
      </v-card>
    </v-col>

    <!-- Column 3 (Voting Clusters and new card) -->
    <v-col cols="12" md="12" class="full-height">
      <v-row>
        <!-- Voting Clusters -->
        <v-col cols="8">
          <v-card class="widget h-100">
            <div class="control-panel-font">Voting Clusters</div>
            <VotingClusters
              :selectedYearRange="selectedYearRange" 
              @cluster-count-updated="updateClusterCount"/>
          </v-card>
        </v-col>
        
        <!-- New Card -->
        <v-col cols="4">
          <v-card style="height: 750px; overflow-y: auto;">
            <div class="control-panel-font">Voting Clusters List</div>
            <!-- Replace the following with your actual component -->
            <ClusterList 
              :selectedYearRange="selectedYearRange"
              :numberOfClusters="numberOfClusters" 
            />
          </v-card>
        </v-col>
      </v-row>
    </v-col>
  </v-row>
</v-container>

    </div>
  </template>

<script>

import ConfigurationPanel from './ConfigurationPanel.vue';
import MostDominatingCountries from './MostDominatingCountries.vue';
import WordCloud from './WordCloud.vue';
import VotingMatrix from './VotingMatrix.vue';
import RankingComparison from './RankingComparison.vue';
import CountryCompositionDisclaimer from './CountryCompositionDisclaimer.vue';
import VotingClusters from './VotingClusters.vue';
import ClusterList from './ClusterList.vue';

export default {
  components: { ConfigurationPanel, CountryCompositionDisclaimer, MostDominatingCountries, WordCloud, VotingMatrix, RankingComparison, VotingClusters, ClusterList},
  data() {
    return {
      selectedYearRange: null,
      numberOfClusters: 5,
    };
  },
  methods: {
    onYearRangeChanged(yearRange) {
      this.selectedYearRange = yearRange; // Update the selected year
    },
    updateClusterCount(newCount) {
      this.numberOfClusters = newCount; // Update the number of clusters
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

  .line-graph-container {
    padding-right: 1px; /* Add padding inside the card */
  }

  </style>
  