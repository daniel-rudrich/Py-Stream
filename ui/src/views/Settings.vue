<template>
  <div class="container home">
    Hallo
    <b-form-select v-model="activeDeck" :options="streamdecksOptions" @change="changeActiveDeck"></b-form-select>
    activeDeck: {{ activeDeck }} <br><br>
    

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
      return this.streamdecks.map(deck => {return {value: deck.id, text: deck.name + ' (S/N: ' + deck.serial_number + ')'}})
    }

  },
  data() {
    return {
      activeDeck: -1,
      streamdecks: [],
      brightness: this.$store.state.decks[0].brightness,
      name: this.$store.state.decks[0].name
    }
  },
  mounted() {
    this.activeDeck = this.$store.state.activeDeck
    axios.get('http://localhost:8000/streamdeck/')
    .then((response) => {
      this.streamdecks = response.data
      if(this.activeDeck === -1 && this.streamdecks.length > 0) {
        this.activeDeck = this.streamdecks[0].id
        //this.brightness = this.streamdecks[0].brightness
      }
    })
    .catch((error) => {
      console.log(error);
    })
    
  },
  methods: {
    changeActiveDeck() {
      this.$store.commit('activeDeck', this.activeDeck)
      console.log("Active deck changed")
    },
    async saveChanges() {
      await axios.put(this.$store.state.decks[0].url, {
          name: this.name,
          serial_number: this.$store.state.decks[0].serial_number,
          brightness: this.brightness,
          streamdeck_model: this.$store.state.decks[0].streamdeck_model
      })
      await this.$store.dispatch('refreshDecks')
    }
  }
}
</script>
