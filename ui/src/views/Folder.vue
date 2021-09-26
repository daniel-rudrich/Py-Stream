<template>
  <div class="container about">
    <br>
    <h1>
      <b-row>
        <b-col cols="1">
          <deck-settings 
              :streamdeckid="this.activeDeck"
              v-on:folder-changed="$emit('folder-changed')">
          </deck-settings>
        </b-col>
        <b-col cols="10">
          <b-form-select v-model="activeDeck" :options="streamdecksOptions" @change="changeActiveDeck" id="streamdeckSelect"></b-form-select>
        </b-col>
      </b-row>
    </h1>
    <br>
    <b-row cols="7">
      <b-col/>
      <b-col/>
      <b-col>
        <p>Brightness: </p>
      </b-col>
      <b-col>
        <b-form-slider ref="basic" id="demo-sb" v-model="brightness" :min="1" :max="100" v-on:change="waitToSave"></b-form-slider>
      </b-col>
      <b-col>
        <p>{{brightness}}</p>
      </b-col>
      <b-col/>
      <b-col/>
    </b-row>
    <br>
    <div v-if="keys.length > 0">
      <div
        class="row justify-content-center"
        v-for="row in $store.getters.deckRows"
        :key="row"
      >
        <div
          class="col-md-auto"
          v-for="col in $store.getters.deckColumns"
          :key="col"
        >
          <deck-btn
            :payload="keys.find(key => key.number === ((row - 1) * $store.getters.deckColumns + col - 1))"
          />
        </div>
      </div>

    </div>

    <br><br>

    <btn-settings
      :payload="keys.find(key => key.id === $store.state.selected)"
      v-on:folder-changed="loadFolder"
    />
  </div>
</template>

<script>
//import store from '@/store'
import DeckBtn from '@/components/DeckBtn.vue'
import BtnSettings from '@/components/BtnSettings.vue'
import DeckSettings from '@/components/DeckSettings.vue'
import axios from 'axios'

export default {
  name: 'Home',
  components: {
    DeckBtn,
    BtnSettings,
    DeckSettings
  },
  data() {
    return {
      name: '',
      keys: [],
      activeDeck: -1,
      brightness: 0,
      waitTime: 500,
    }
  },
  computed: {
    streamdecksOptions() {
      return this.$store.state.decks.map(deck => {return {value: deck.id, text: deck.name + ' (S/N: ' + deck.serial_number + ')'}})
    }

  },
  mounted() {
    this.loadFolder()
    this.activeDeck = this.$store.state.activeDeck
    const active = this.$store.getters.activeDeck
    this.brightness = active.brightness
  },
  methods: {
    async loadFolder() {
      const folderId = this.$route.params.folder || 1
      if(this.$store.getters.activeDeckDefaultFolder === folderId) {
        const folder = await axios.get('streamdecks/' + this.$store.state.activeDeck + '/folders/' + folderId)
        this.name = folder.data.name
        this.keys = folder.data.keys
        if(this.keys.find(key => key.id === this.$store.state.selected) === undefined) {
          this.$store.commit('selectKey', this.keys[0].id)
        }
      } else {
        let folder
        try {
          folder = await axios.get('streamdecks/' + this.$store.state.activeDeck + '/folders/' + folderId)
        } catch(err) {
          console.log('pushing to ' + '/' + this.$store.getters.activeDeckDefaultFolder)
          this.$router.push('/' + this.$store.getters.activeDeckDefaultFolder)
          return
        }
        this.name = folder.data.name
        this.keys = folder.data.keys
        if(this.keys.find(key => key.id === this.$store.state.selected) === undefined) {
          this.$store.commit('selectKey', this.keys[0].id)
        }
      }
      
    },
    changeActiveDeck() {
      this.$store.commit('activeDeck', this.activeDeck)
      this.loadFolder()
      console.log("Active deck changed")
    },
    waitToSave(){
        // Unset previous timeout.
        clearTimeout(this.timeout);
        // Set current timeout.
        // If no further changes after 1 second, then save the change.
        this.timeout = setTimeout(function(){this.saveChanges()}.bind(this), this.waitTime);
    },

    async saveChanges() {
      await axios.patch('streamdecks/' + this.activeDeck, {
          brightness: this.brightness,
      })
      await this.$store.dispatch('refreshDecks')
    },
  },
  watch: {
    "$route.params.folder"() {
      this.loadFolder()
    },
},
  
}
</script>
<style scoped>
  #streamdeckSelect{
    background-color: #212121;
    color: white;
    border: none;
    font-size: 25px;
  }
  .custom-select{
    background: #212121 url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' width='4' height='5' viewBox='0 0 4 5'%3e%3cpath fill='white' d='M2 0L0 2h4zm0 5L0 3h4z'/%3e%3c/svg%3e") no-repeat right .75rem center/8px 10px !important;
  }
</style>
