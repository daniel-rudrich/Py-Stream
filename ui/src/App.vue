<template>
  <div id="app" v-if="loaded">
    <router-view/>
  </div>
</template>

<script>

export default {
  data() {
    return {
      loaded: false,
    }
  },
  async mounted() {
    await this.$store.dispatch('initialize')
    this.loaded = true
//this.$store.commit('set', ['models', response.data])
    //this.loadModels()
  },
  methods: {
    
  }
}
</script>

<style>
html {
  background-color: #212121;
}
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #ffffff;
  background-color: #212121;
}

#nav {
  padding: 30px;
}

#nav a {
  font-weight: bold;
  color: #007bff
}

#nav a.router-link-exact-active {
  color: #3194ff;
}
</style>
