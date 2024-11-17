<template>
  <v-app>
    <v-main>
      <MainContainer/>
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
import MainContainer from './components/MainContainer.vue';
// import ConfigurationPanel from './components/ConfigurationPanel.vue';

export default {
  name: 'App',

  components: {
    MainContainer,
  },

  data: () => ({
    //
  }),
}
</script>
