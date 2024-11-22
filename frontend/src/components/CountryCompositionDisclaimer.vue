<template>
  <div class="disclaimer-container">
    <h3 @click="toggleCollapse" class="collapsible-header">
      Historical Changes in Country Composition (1957 - 2023)
      <span class="toggle-icon">{{ isCollapsed ? "▼" : "▲" }}</span>
    </h3>
    <ul v-show="isCollapsed">
      <li v-for="(change, index) in countryChanges" :key="index">
        <p>{{ change.message }}</p>
        <div class="country-info">
          <strong>Countries:</strong>
          <div v-if="change.countries.splitFrom.length > 0">
            <strong>From:</strong>
            <span v-for="(country, idx) in change.countries.splitFrom" :key="idx">
              <span class="country-code" :title="country.name">
                {{ country.name }} ({{ country.code }})
              </span>
              <span v-if="idx < change.countries.splitFrom.length - 1">, </span>
            </span>
          </div>
          <div v-if="change.countries.splitTo.length > 0">
            <strong>To:</strong>
            <span v-for="(country, idx) in change.countries.splitTo" :key="idx">
              <span class="country-code" :title="country.name">
                {{ country.name }} ({{ country.code }})
              </span>
              <span v-if="idx < change.countries.splitTo.length - 1">, </span>
            </span>
          </div>
        </div>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  data() {
    return {
      isCollapsed: false, // Controls whether the list is collapsed
      countryChanges: [
        {
          startYear: 1960,
          endYear: null,
          message: "Many African nations gained independence from colonial powers in 1960, known as the Year of Africa.",
          countries: {
            splitFrom: [
              { name: "France", code: "FR" },
              { name: "Belgium", code: "BE" },
              { name: "United Kingdom", code: "GB" }
            ],
            splitTo: [
              { name: "Senegal", code: "SN" },
              { name: "Ivory Coast", code: "CI" },
              { name: "Nigeria", code: "NG" },
              { name: "Congo", code: "CG" },
              { name: "Chad", code: "TD" }
            ]
          }
        },
        {
          startYear: 1991,
          endYear: null,
          message: "The Soviet Union dissolved in 1991, leading to the independence of 15 countries.",
          countries: {
            splitFrom: [{ name: "Soviet Union", code: "SU" }],
            splitTo: [
              { name: "Russia", code: "RU" },
              { name: "Ukraine", code: "UA" },
              { name: "Belarus", code: "BY" },
              { name: "Estonia", code: "EE" },
              { name: "Latvia", code: "LV" },
              { name: "Lithuania", code: "LT" },
              { name: "Moldova", code: "MD" },
              { name: "Armenia", code: "AM" },
              { name: "Azerbaijan", code: "AZ" },
              { name: "Georgia", code: "GE" },
              { name: "Kazakhstan", code: "KZ" },
              { name: "Kyrgyzstan", code: "KG" },
              { name: "Tajikistan", code: "TJ" },
              { name: "Turkmenistan", code: "TM" },
              { name: "Uzbekistan", code: "UZ" }
            ]
          }
        },
        {
          startYear: 1992,
          endYear: null,
          message: "Yugoslavia dissolved in 1992, leading to the formation of several independent states.",
          countries: {
            splitFrom: [{ name: "Yugoslavia", code: "YU" }],
            splitTo: [
              { name: "Slovenia", code: "SI" },
              { name: "Croatia", code: "HR" },
              { name: "Bosnia and Herzegovina", code: "BA" },
              { name: "Macedonia", code: "MK" },
              { name: "Serbia and Montenegro", code: "CS" }
            ]
          }
        },
        {
          startYear: 1993,
          endYear: null,
          message: "Czechoslovakia split into the Czech Republic and Slovakia in 1993.",
          countries: {
            splitFrom: [{ name: "Czechoslovakia", code: "CS" }],
            splitTo: [
              { name: "Czech Republic", code: "CZ" },
              { name: "Slovakia", code: "SK" }
            ]
          }
        },
        {
          startYear: 2006,
          endYear: null,
          message: "Montenegro declared independence from Serbia and Montenegro in 2006.",
          countries: {
            splitFrom: [{ name: "Serbia and Montenegro", code: "CS" }],
            splitTo: [
              { name: "Montenegro", code: "ME" },
              { name: "Serbia", code: "RS" }
            ]
          }
        },
        {
          startYear: 2008,
          endYear: null,
          message: "Kosovo declared independence from Serbia in 2008.",
          countries: {
            splitFrom: [{ name: "Serbia", code: "RS" }],
            splitTo: [{ name: "Kosovo", code: "XK" }]
          }
        },
        {
          startYear: 2011,
          endYear: null,
          message: "South Sudan declared independence from Sudan in 2011 after a long civil war.",
          countries: {
            splitFrom: [{ name: "Sudan", code: "SD" }],
            splitTo: [{ name: "South Sudan", code: "SS" }]
          }
        }
      ]
    };
  },
  methods: {
    toggleCollapse() {
      this.isCollapsed = !this.isCollapsed;
    }
  }
};
</script>

<style>
.disclaimer-container {
  background-color: #fff3cd;
  border: 1px solid #ffeeba;
  padding: 10px;
  margin: 10px 0;
  border-radius: 5px;
  font-size: 14px;
}
.disclaimer-container h3 {
  margin: 0 0 10px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.collapsible-header:hover {
  color: #0056b3;
}
.toggle-icon {
  font-size: 16px;
  margin-left: 10px;
}
.country-code {
  background-color: #e2e3e5;
  border-radius: 3px;
  padding: 2px 4px;
  margin: 0 2px;
  font-size: 12px;
}
</style>
