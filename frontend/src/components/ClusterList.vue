<template>
    <div>
      <v-card>
        <v-card-text>
          <ul>
            <!-- Render clusters and countries -->
            <li v-for="(countries, cluster) in groupedClusters" :key="cluster">
              <strong>Cluster {{ parseInt(cluster) + 1 }}</strong>
              <ul>
                <li v-for="country in countries" :key="country">
                  {{ country }}
                </li>
              </ul>
            </li>
          </ul>
        </v-card-text>
      </v-card>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  
  export default {
    props: ["selectedYearRange", "numberOfClusters"], // Accept year range as a prop
    data() {
      return {
        clusterData: [], // Store raw cluster data from the backend
        groupedClusters: {}, // Store grouped clusters for display
      };
    },

    mounted() {
        // Trigger the API call on component load
        this.fetchClusterData(this.numberOfClusters);
        console.log("ClusterList mounted with numberOfClusters:", this.numberOfClusters);
    },

    watch: {
        selectedYearRange: {
            immediate: true, // React immediately on component load
            handler() {
              this.fetchClusterData();
            },
        },
        numberOfClusters: {
            immediate: true, // React immediately to numberOfClusters changes
            handler(newCount) {
            console.log("Number of clusters updated in ClusterList:", newCount);
            this.fetchClusterData(newCount); // Fetch updated cluster data
            },
        },
        },
    methods: {
      async fetchClusterData(newCount = this.numberOfClusters || 5) {
        try {
          const response = await axios.get("http://127.0.0.1:5000/api/voting_clusters_fullname", {
            params: {
              yearRangeStart: this.selectedYearRange[0],
              yearRangeEnd: this.selectedYearRange[1],
              numberOfClusters: newCount,
            },
          });
          this.clusterData = response.data;
          this.groupClusters();
        } catch (error) {
          console.error("Error fetching cluster data:", error);
        }
      },
      groupClusters() {
        // Group countries by their cluster ID
        this.groupedClusters = this.clusterData.reduce((acc, item) => {
          if (!acc[item.cluster]) {
            acc[item.cluster] = [];
          }
          acc[item.cluster].push(item.country);
          return acc;
        }, {});
      },
    },
  };
  </script>
  
  <style scoped>
  ul {
    list-style-type: none; /* Remove default list styling */
    padding: 0;
  }
  
  li {
    margin-bottom: 5px; /* Add spacing between items */
  }
  
  strong {
    font-size: 16px;
    color: #333; /* Make cluster titles bold and distinct */
  }
  </style>