<template>
  <div v-if="payload">
    <h4><img :src="image" style="height: 30px;">Button #{{ payload.id }}</h4>
    <br>
    <b-form-input v-model="payload.text" placeholder="Enter key text"></b-form-input>
    <br>
    <b-button variant="success" @click="saveChanges">Save</b-button>
    <br>
    <br>
    <h3>Commands</h3>
    <div v-for="command in commands" :key="command.id">
        {{ command.name }}: "{{ command.command_string }}"<br>
    </div>
    <b-button variant="primary" @click="saveChanges">Add command</b-button>

    <br>
    <br>
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
    }
  },
  mounted() {
  },
  computed: {
    commands() {
      const commands = []
      let next = this.payload.command
      while(next) {
        commands.push(next)
        next = next.following_command
      }
      return commands
    },
    image() {
      if(this.payload.image_source === null) return 'https://www.elgato.com/themes/custom/smalcode/key-creator/assets/image_pool/sd31/btn_custom_trigger_hotkey2.svg'
      return 'http://localhost:8000' + this.payload.image_source
    }
  },
  methods: {
      async saveChanges() {
        await axios.patch('key/' + this.payload.id, {
            text: this.payload.text,
            image_source: null
        })
        // TODO: Refresh displayed text
        await this.$store.dispatch('refresh')
      }
  }
}
</script>