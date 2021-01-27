<template>
  <div class="container about">
    <h1>{{ $store.getters.selectedModel.name }}</h1>

    <div>
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
            v-if="$store.state.keys.find(key => key.number === ((row - 1) * $store.getters.deckColumns + col - 1))"
            :payload="$store.state.keys.find(key => key.number === ((row - 1) * $store.getters.deckColumns + col - 1))"
          />
        </div>
      </div>

    </div>

    <br><br>

    <btn-settings
      :payload="$store.state.keys.find(key => key.id === $store.state.selected)"
    
    />

      
    
  </div>
</template>

<script>
//import store from '@/store'
import DeckBtn from '@/components/DeckBtn.vue'
import BtnSettings from '@/components/BtnSettings.vue'


export default {
  name: 'Home',
  components: {
    DeckBtn,
    BtnSettings
  },
  data() {
    return {
      small: true,
      streamdecks: []
    }
  },
  
}
</script>
