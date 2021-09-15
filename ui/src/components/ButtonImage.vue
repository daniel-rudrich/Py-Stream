<template>
  <div v-if="payload && this.original_image != 'None'">
    <div v-if="this.animated">
      <img :src="this.original_image" style="height: 80px; border-radius: 13px;">
    </div>
    <div v-else>
      <img :src="'data:image/jpeg;base64,' + this.original_image" style="height: 80px; border-radius: 13px;">
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'BtnSettings',
  props: [
      'payload',
  ],
  watch:{
    payload: function(){
      this.getImage()
    }
  },
  data() {
    return {
      original_image: null,
      animated: false,
    }
  },
  created() {
    this.getImage()
  },
  methods: {
      getImage(){
          if (this.payload.image_source != null && this.payload.image_source.slice(-4) === '.gif'){
            this.animated = true
            this.original_image = 'http://localhost:8000' + this.payload.image_source
          }else{
            this.animated = false
            axios.get('key/' + this.payload.id + '/image').then((response) => (this.original_image = response.data))
          }
          
      },
  }
}
</script>