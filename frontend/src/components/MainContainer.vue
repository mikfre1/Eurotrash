<template>
  <div class="main-container">
    <!-- Sidebar Navigation -->
    <div class="sidebar">
      <div class="logo">Eurotrash</div>
      <ul class="nav-list">
        <li class="nav-item" @click="setPage('Performance')" :class="{ active: currentPage === 'Performance' }">
          Performance
        </li>
        <li class="nav-item" @click="setPage('Voting Patterns')" :class="{ active: currentPage === 'Voting Patterns' }">
          Voting Patterns
        </li>
        <li class="nav-item" @click="setPage('Fun')" :class="{ active: currentPage === 'Fun' }">
          Fun
        </li>
      </ul>
    </div>

    <!-- Main Content Section -->
    <div class="content">
      <!-- Pass currentPage and selectedCountries to ConfigurationPanel -->
      <ConfigurationPanel
        :current-page="currentPage"
        :selected-countries="selectedCountries"
        @update-selected-countries="updateSelectedCountries"
        @year-range-changed="onYearRangeChanged" />
      <CountryCompositionDisclaimer />

      <v-container fluid class="full-height">
        <v-row class="full-height">
          <!-- Performance Page -->
          <template v-if="currentPage === 'Performance'">
            <v-container fluid class="pa-0">
              <!-- First Row -->
              <v-row class="pa-0">
                <v-col cols="12" md="6" class="pa-0">
                  <v-card class="widget">
                    <div class="control-panel-font">Ranking Comparison</div>
                    <RankingComparison :selectedCountries="selectedCountries" :selectedYearRange="selectedYearRange" />
                  </v-card>
                </v-col>

                <v-col cols="12" md="6" class="pa-0">
                  <v-card class="widget">
                    <div class="control-panel-font">Most Dominating Countries</div>
                    <MostDominatingCountries :selectedYearRange="selectedYearRange" />
                  </v-card>
                </v-col>
              </v-row>

              <!-- Second Row -->
              <v-row class="pa-0">
                <v-col cols="12" class="pa-0">
                  <v-card class="widget">
                    <div class="control-panel-font">Voting Heatmap</div>
                    <VotingMatrix :selectedYearRange="selectedYearRange" />
                  </v-card>
                </v-col>
              </v-row>
            </v-container>

          </template>

          <!-- Voting Patterns Page -->
          <template v-if="currentPage === 'Voting Patterns'">
            <v-col cols="12" md="12" class="full-height">
              <v-card class="widget mb-4">
                <div class="control-panel-font">Voting Clusters</div>
                <VotingClusters :selectedYearRange="selectedYearRange" />
              </v-card>
            </v-col>
          </template>

          <!-- Fun Page -->
          <template v-if="currentPage === 'Fun'">
            <v-col cols="12" md="6" class="full-height">
              <v-card class="widget mb-4">
                <div class="control-panel-font">Word Cloud</div>
                <WordCloud :selectedYearRange="selectedYearRange" />
              </v-card>
            </v-col>

            <v-col cols="12" md="6" class="full-height">
              <v-card class="widget mb-4">
                <div class="control-panel-font">Fun Widget</div>
                <p> Placeholder Youtube Vid Widget</p>
              </v-card>
            </v-col>
          </template>
        </v-row>
      </v-container>
    </div>
  </div>
</template>

<script>
import ConfigurationPanel from "./ConfigurationPanel.vue";
import MostDominatingCountries from "./MostDominatingCountries.vue";
import WordCloud from "./WordCloud.vue";
import VotingClusters from "./VotingClusters.vue";
import RankingComparison from "./RankingComparison.vue";
import CountryCompositionDisclaimer from "./CountryCompositionDisclaimer.vue";
import VotingMatrix from "./VotingMatrix.vue";

export default {
  components: {
    ConfigurationPanel,
    CountryCompositionDisclaimer,
    MostDominatingCountries,
    WordCloud,
    VotingClusters,
    RankingComparison,
    VotingMatrix,
  },
  data() {
    return {
      selectedYearRange: null,
      currentPage: "Performance", // Default Page
      selectedCountries: ["Sweden", "Italy"], // Default selected countries
    };
  },
  methods: {
    onYearRangeChanged(yearRange) {
      this.selectedYearRange = yearRange; // Update the selected year range
    },
    setPage(page) {
      this.currentPage = page;
    },
    updateSelectedCountries(countries) {
      this.selectedCountries = countries; // Update selected countries
    },
  },
};
</script>

<style>
/* Main container styling */

:root {
  --base-color: #1a1a1a; /* Base dark theme color */
  --highlight-color: #171717; /* Slightly brighter for navigation bar */
  --content-bg-color: #1e1f22; /* Darker content background */
  --text-color: #ffffff; /* White text for contrast */
  --hover-color: #3a3a3a; /* Brighter hover state */
}

.full-height {
  height: auto; /* Fill the parent's height */
}

/* Main container styling */
.main-container {
  display: flex;
  min-height: 100vh; /* Use min-height to allow scrolling */
  height: auto;
  background-color: var(--content-bg-color); /* Darker background for content */
  color: var(--text-color);
}

/* Sidebar styling */
.sidebar {
  background: linear-gradient(to right, var(--highlight-color), var(--content-bg-color));
  color: var(--text-color);
  width: 250px;
  display: flex;
  flex-direction: column;
  padding: 20px;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.2);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
}

/* Content styling */
.content {
  flex-grow: 1;
  overflow-y: auto; /* Enable scrolling for overflowing content */
  padding: 20px;
  background-color: var(--content-bg-color);
  color: var(--text-color);
}


/* Logo styling */
.logo {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 20px;
  text-align: center;
  text-transform: uppercase;
  letter-spacing: 2px;
  color: var(--text-color);
}

/* Navigation list styling */
.nav-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-item {
  margin: 10px 0;
  cursor: pointer;
  padding: 10px;
  border-radius: 5px;
  transition: background-color 0.3s, transform 0.2s;
}

.nav-item:hover {
  background-color: var(--hover-color); /* Brighter hover state */
  transform: scale(1.05); /* Subtle zoom effect */
}

.nav-item.active {
  background-color: var(--base-color); /* Match base dark color for active state */
  font-weight: bold;
  border-left: 4px solid var(--text-color); /* Indicator for active page */
}



/* Widgets styling */
.widget {
  background-color: var(--base-color); /* Match base theme for widgets */
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* Subtle shadow */
  color: var(--text-color);
}
</style>


