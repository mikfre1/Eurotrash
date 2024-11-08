<template>
  <div>
    <v-container fluid>
      <v-row>
        <v-col cols="12" md="2" class="sideBar">
          <v-card>
            <v-row>
              <v-col cols="12" sm="12">
                <div class="control-panel-font">Company Overview</div>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12" sm="12">
                <v-select
                    :items="categories.values"
                    label="Select a category"
                    dense
                    v-model="categories.selectedValue"
                    @change="changeCategory"
                ></v-select>

              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12" sm="12">
                <div class="control-panel-font">Profit View</div>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12" sm="12">
                <v-select
                    :items="companies.values"
                    item-value="id"
                    item-title="name"
                    label="Select a company"
                    dense
                    v-model="companies.selectedValue"
                    @change="changeCompany"
                ></v-select>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12" sm="12">
                <v-select
                    :items="algorithm.values"
                    label="Select an algorithm"
                    dense
                    v-model="algorithm.selectedValue"
                    @change="changeAlgorithm"
                ></v-select>
              </v-col>
            </v-row>
          </v-card>
        </v-col>
        <v-col cols="12" md="5">
          <ScatterPlot :key="scatterPlotId"
                       :selectedCategory="categories.selectedValue"
                       @changeCurrentlySelectedCompany="changeCurrentlySelectedCompany"
                       @changeSelectedCategory="changeSelectedCategory"
          />
        </v-col>
        <v-col cols="12" md="5">
          <LinePlot :key="linePlotId"
                    :selectedCompanyName="companies.selectedName"
                    :selectedCompany="companies.selectedValue"
                    :selectedAlgorithm="algorithm.selectedValue"
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="6">
          <BarPlot :key="barPlotId" :selectedCategory="categories.selectedValue" />
        </v-col>

        <v-col cols="6">
          <v-row v-if="poem && fact">
            <v-col cols="12">
              <div class="control-panel-font"><strong>Poem of Company {{this.companies.selectedName}}:</strong></div>
              <p>{{ poem }}</p>
            </v-col>

            <v-col cols="12">
              <div class="control-panel-font"><strong>3 Facts about Company {{this.companies.selectedName}}:</strong></div>
              <p>{{ fact }}</p>
            </v-col>
          </v-row>
        </v-col>
      </v-row>

    </v-container>
  </div>
</template>


<script>
import ScatterPlot from './ScatterPlot';
import LinePlot from './LinePlot';
import BarPlot from "./BarPlot.vue";
export default {
  components: {BarPlot, ScatterPlot, LinePlot},
  data: () => ({
    scatterPlotId: 0,
    linePlotId: 0,
    multiPlotId: 0,
    categories: {
      values: ['All', 'tech', 'health', 'bank'],
      selectedValue: 'All'
    },
    poem: "",
    fact:"",
    companies: {
      values: [],
      selectedValue: 1,
      selectedName: "none"
    },
    algorithm: {
      values: ['none', 'random', 'regression'],
      selectedValue: 'none'
    }
  }),

  watch: { 'categories.selectedValue': function () {    this.changeCategory();  },  'companies.selectedValue': function () {    this.changeCompany();  },  'algorithm.selectedValue': function () {    this.changeAlgorithm();  }},
  mounted() {
    console.log("mounted in ConfigPanel entred")
    console.log("before fetch poeam")
    this.fetchPoem(1)
    console.log("after fetch poeam")
    this.fetchfacts(1)
    this.fetchData()
  },

  methods: {
    async fetchData() {
      var reqUrl = 'http://127.0.0.1:5000/companies?category=All';
      var response = await fetch(reqUrl);
      var responseData = await response.json();

      // Store companies as {id, name} pairs
      responseData.forEach((company) => {
        this.companies.values.push({ id: company.id, name: company.name });
      });
      this.companies.selectedName = this.companies.values.find(company => company.id === this.companies.selectedValue).name;
    },

    changeCategory() {
      this.scatterPlotId += 1
      this.barPlotId += 1
    },
    changeCompany() {
      this.linePlotId += 1
      console.log("ChangeCompany used")
      this.companies.selectedName = this.companies.values.find(company => company.id === this.companies.selectedValue).name;
      this.fetchPoem(this.companies.selectedValue);
      this.fetchfacts(this.companies.selectedValue);

    },
    changeAlgorithm() {
      this.linePlotId += 1
    },
    changeCurrentlySelectedCompany(companyId) {
      this.companies.selectedValue = companyId
      this.companies.selectedName = this.companies.values.find(company => company.id === this.companies.selectedValue).name;
      this.changeCompany()
    },
    changeSelectedCategory(category) {
      this.categories.selectedValue = category;
      this.barPlotId += 1; // Trigger the BarPlot to update
    },
    async fetchPoem(companyId) {
      try {
        const response = await fetch(`http://localhost:5000/groq/poem/${companyId}`);
        const responseData = await response.json();
        console.log("ResponseData",responseData)
        this.poem = responseData.result;
        console.log("fetchPoem executed", this.poem);
      } catch (error) {
        console.error("Error fetching the poem:", error);
      }
    },
    async fetchfacts(companyId) {
      try {
        const response = await fetch(`http://localhost:5000/groq/fact/${companyId}`);
        const responseData = await response.json();
        console.log("ResponseData",responseData)
        this.fact = responseData.result;
      } catch (error) {
        console.error("Error fetching the poem:", error);
      }
    }

  },


}
</script>

<style scoped>
.control-panel-font {
  font-family: "Open Sans", verdana, arial, sans-serif;
  align-items: center;
  font-size: 18px;
  //border-bottom: 1px solid rgba(0, 0, 0, 0.1); /* enables thin line under Company view and Profit view */
  display: flex;
  font-weight: 600;
  height: 40px;
  padding-bottom: 5px; /* Adds space under the text */
}

.sideBar {
  //border-right: 1px solid rgba(0, 0, 0, 0.1); /* Thin line along Graph */
  background: transparent;
  padding-left: 17px;
  height: calc(100vh - 50px);
}
</style>
