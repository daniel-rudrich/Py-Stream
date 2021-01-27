<template>
  <div>
    <h3><img :src="payload.image_source" style="height: 30px;"> {{ payload.text }}</h3>
    
    
    <br>
    <b-form-input v-model="text" placeholder="Enter key text"></b-form-input>
    <br>
    <b-button variant="success" @click="saveChanges">Save</b-button>
    <br>
    <br>
    <h3>Commands</h3>
    <div v-for="command in $store.getters.selectedCommands" :key="command.id">
        {{ command.name }}: "{{ command.command_string }}"<br>
    </div>

    {{ payload }}
  </div>
  
  
</template>

<script>
import axios from 'axios'

export default {
  name: 'BtnSettings',
  props: [
      'payload'
  ],
  data() {
    return {
       text: ''
    }
  },
  mounted() {
      this.text = this.payload.text
  },
  methods: {
      async saveChanges() {
        await axios.put(this.payload.url, {
            text: this.text,
            number: this.payload.number,
            folder: this.payload.folder,
            streamdeck: this.payload.streamdeck
        })
        await this.$store.dispatch('refreshKeys')
      }
  }
}
</script>