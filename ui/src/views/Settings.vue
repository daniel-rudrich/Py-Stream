<template>
  <div class="container home">
    <b-form-select v-model="activeDeck" :options="streamdecksOptions" @change="changeActiveDeck"></b-form-select>
    activeDeck: {{ $store.state.activeDeck }} <br><br>

    <br><br>
    <b-form-spinbutton id="demo-sb" v-model="brightness" min="1" max="100"></b-form-spinbutton><br>
    <b-form-input v-model="name" placeholder="Enter name"></b-form-input>

    <br>
    <b-button variant="success" @click="saveChanges">Save</b-button>
  </div>
</template>

<script>
// @ is an alias to /src
import axios from 'axios'

export default {
  name: 'Home',
  components: {
  },
  computed: {
    streamdecksOptions() {
      return this.$store.state.decks.map(deck => {return {value: deck.id, text: deck.name + ' (S/N: ' + deck.serial_number + ')'}})
    }

  },
  data() {
    return {
      activeDeck: -1,
      brightness: 0,
      name: ''
    }
  },
  mounted() {
    this.activeDeck = this.$store.state.activeDeck
    const active = this.$store.getters.activeDeck
    this.brightness = active.brightness
    this.name = active.name
  },
  methods: {
    changeActiveDeck() {
      this.$store.commit('activeDeck', this.activeDeck)
      console.log("Active deck changed")
    },
    async saveChanges() {
      await axios.patch('streamdecks/' + this.activeDeck, {
          name: this.name,
          brightness: this.brightness,
      })
      await this.$store.dispatch('refreshDecks')
    }
  }
}
</script>
