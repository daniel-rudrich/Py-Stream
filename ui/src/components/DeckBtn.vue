<template>
  <div>
    <div
      id="deck-btn"
      :style="[$store.getters.selected !== payload.id ?
      {border: '1.5px solid black'} :
      {border: '4px solid red'}]"
      @click="$store.commit('selectKey', payload.id)"
    >
      <img :src="payload.image_source" style="max-width:100%; max-height:100%;">
      
    </div>
    {{ payload.text || 'none' }}
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
