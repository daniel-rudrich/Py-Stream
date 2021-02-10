<template>
  <div v-if="payload">
    <div
      id="deck-btn"
      :style="[$store.getters.selected !== payload.id ?
      {border: '1.5px solid black'} :
      {border: '4px solid red'}]"
      @click="keyClicked"
    > 
      <img
        :src="image"
        style="max-width:100%; max-height:100%;"
      >
    </div>
    <span
      :style="[payload.change_to_folder ?
      {color: 'blue'} :
      {}]"
    >
      {{ payload.text || 'None' }}
    </span>
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

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
#deck-btn {
    height: 70px;
    width: 70px;
    border-radius: 13px;
    margin-bottom: 15px;
    /*background-image: url('https://www.elgato.com/themes/custom/smalcode/key-creator/assets/image_pool/sd3/btn_custom_folder.svg');*/
    background-position: center; /* Center the image */
    background-repeat: no-repeat; /* Do not repeat the image */
    background-size: cover; /* Resize the background image to cover the entire container */
}
</style>
