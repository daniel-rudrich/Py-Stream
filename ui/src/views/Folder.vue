<template>
  <div class="container about">
    <h1>{{ $store.getters.activeDeck.name }}</h1>


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
    
    />

      
    
  </div>
</template>

<script>
//import store from '@/store'
import DeckBtn from '@/components/DeckBtn.vue'
import BtnSettings from '@/components/BtnSettings.vue'
import axios from 'axios'

export default {
  name: 'Home',
  components: {
    DeckBtn,
    BtnSettings
  },
  data() {
    return {
      name: '',
      keys: []
    }
  },
  mounted() {
    this.loadFolder()
  },
  methods: {
    async loadFolder() {
      const folderId = this.$route.params.folder || 1
      const folder = await axios.get('streamdecks/' + this.$store.state.activeDeck + '/folders/' + folderId)
      this.name = folder.data.name
      this.keys = folder.data.keys
      if(this.keys.find(key => key.id === this.$store.state.selected) === undefined) {
        this.$store.commit('selectKey', this.keys[0].id)
      }
    }
  },
  watch: {
    "$route.params.folder"() {
      this.loadFolder()
    },
},
  
}
</script>
