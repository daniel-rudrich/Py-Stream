<template>
  <div v-if="payload">
    <div
          id="deck-btn"
          :style="[$store.getters.selected !== payload.id ?
          {border: '2px solid black'} :
          {border: '4px solid #007bff'}]"
          @click="keyClicked"
        > 
      <div class="d-flex flex-column">
        <div>
          
            <img
              :src="image"
              style="max-width:65%; max-height:65%;"
            >
            
        </div>
        <div>
          <span>
              {{ payload.text }}
          </span>
        </div>
      </div>
    
    </div>
  </div>
  
</template>

<script>
export default {
  name: 'DeckBtn',
  props: [
    'payload'
  ],
  data() {
    return {
    }
  },
  computed: {
    image() {
      if(this.payload.image_source === null) return 'https://www.elgato.com/themes/custom/smalcode/key-creator/assets/image_pool/sd31/btn_custom_trigger_hotkey2.svg'
      return 'http://localhost:8000' + this.payload.image_source
    },
  },
  methods: {
    keyClicked() {
      if(this.$store.getters.selected === this.payload.id && this.payload.change_to_folder) {
        this.$router.push('/' + this.payload.change_to_folder.id)
      } else {
        this.$store.commit('selectKey', this.payload.id)
      }
    }
  }
}
</script>

<style scoped>
#deck-btn {
    height: 80px;
    width: 80px;
    border-radius: 13px;
    margin-bottom: 20px;
    background-position: center; /* Center the image */
    background-repeat: no-repeat; /* Do not repeat the image */
    background-size: cover; /* Resize the background image to cover the entire container */
    background-color: #313131;
    overflow-x: hidden;
}
</style>
