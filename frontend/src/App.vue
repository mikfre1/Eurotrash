<template>
  <v-app>
    <v-app-bar app color="blue-grey">
      <h2>Mike Jason Frei 20-488-144</h2>
    </v-app-bar>
    <v-main>
      <ConfigurationPanel/>
    </v-main>
  </v-app>
</template>

<!--npm run serve-->

<style>
/* disable scrolling */
html {
  scrollbar-width: none; /* For Firefox */
  -ms-overflow-style: none; /* For Internet Explorer and Edge */
}
html::-webkit-scrollbar {
  width: 0px; /* For Chrome, Safari, and Opera */
}
</style>


<script>
import ConfigurationPanel from './components/ConfigurationPanel'

export default {
  name: 'App',

  components: {
    ConfigurationPanel,
  },

  data: () => ({
    //
  }),
}
</script>
