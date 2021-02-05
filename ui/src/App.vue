<template>
  <div id="app" v-if="loaded">
    <div id="nav">
      <router-link to="/1">StreamDeck</router-link> |
      <router-link to="/settings">Settings</router-link>
      
    </div>
    <router-view/>
  </div>
</template>

<script>
import axios from 'axios'

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
    async loadModels() {
      axios.get('http://localhost:8000/streamdeckmodel/')
        .then((response) => {
          this.$store.commit('set', ['models', response.data])
        })
        .catch((error) => {
          console.log(error);
        })
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

#nav {
  padding: 30px;
}

#nav a {
  font-weight: bold;
  color: #2c3e50;
}

#nav a.router-link-exact-active {
  color: #42b983;
}
</style>
