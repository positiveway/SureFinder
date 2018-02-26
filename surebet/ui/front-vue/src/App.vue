<template>
  <div id="app">
    <md-toolbar class="md-accent" md-elevation="1">
      <h3 class="md-title" style="flex: 1">Bets</h3>
    </md-toolbar>
    <TableForks/>
  </div>
</template>

<script>
  import TableForks from './components/TableForks.vue'
  
  export default {
    name: 'app',
    components: {
      TableForks
    }
  }
</script>

<style>
  #app {
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    color: #2c3e50;

  }
</style>
