<template>
  <div v-if="payload">
    <div
          id="deck-btn"
          :style="[$store.getters.selected !== payload.id ?
          {} :
          {border: '4px solid #007bff'}]"
          @click="keyClicked"
        > 
      <div class="d-flex flex-column">
        <buttonImage :payload="payload"></buttonImage>
      </div>
    
    </div>
  </div>
  
</template>

<script>
import ButtonImage from './ButtonImage.vue'

export default {
  name: 'DeckBtn',
  props: [
    'payload',
  ],
  components: {
    ButtonImage,
  },
  data() {
    return {
    }
  },
  methods: {
    keyClicked() {
      if(this.$store.getters.selected === this.payload.id && this.payload.change_to_folder) {
        this.$router.push({name: "Folder", params: {folder: this.payload.change_to_folder.id}})
      } else {
        this.$store.commit('selectKey', this.payload.id)
      }
    },
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
    overflow-y: hidden;
}
</style>
