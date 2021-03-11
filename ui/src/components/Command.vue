<template>
  <div v-if="payload">
    <b-row v-if="payload.command_type === 'shell'">
      <b-col>
          {{ payload.command_type }}
      </b-col>
      <b-col cols="4">
          <b-form-input v-model="payload.name" placeholder="Command name"></b-form-input>
      </b-col>
      <b-col  cols="4">
          <b-form-input v-model="payload.command_string" placeholder="Command"></b-form-input>
      </b-col>
      <b-col>
          <b-button variant="success" size="sm" @click="saveChanges">Save</b-button>
          &nbsp;
          <b-button variant="danger" size="sm" @click="deleteCommand">Delete</b-button>
      </b-col>
    </b-row>
    <b-row v-if="payload.command_type === 'hotkey'">
      <b-col>
        {{ payload.command_type }}
      </b-col>
      <b-col cols="4">
        <b-form-input v-model="payload.name" placeholder="Command name"></b-form-input>
      </b-col>
      <b-col  cols="4">
        <b-form-input :placeholder="keys" @keydown="keydown($event)" @keyup="keyup($event)"></b-form-input>
        {{ keys }}
      </b-col>
      <b-col>
        <b-button variant="success" size="sm" @click="saveChanges">Save</b-button>
        &nbsp;
        <b-button variant="danger" size="sm" @click="deleteCommand">Delete</b-button>
      </b-col>
    </b-row>
  </div> 
</template>

<script>
import axios from 'axios'

export default {
  name: 'Command',
  props: [
      'keyid',
      'payload'
  ],
  data() {
    return {
      newCommandKeys: {
        finished: true,
        pressed: [],
        pressedString: [],
        first: null,
      }
    }
  },
  mounted() {
    
  },
  computed: {
    keys() {
      if(this.newCommandKeys.pressedString.length > 0) {
        let keys = ''
        this.newCommandKeys.pressedString.forEach(element => keys += ' + ' + element)
        return keys
      } else {
        let keys = ''
        if(this.payload.hotkeys.key1) keys += this.payload.hotkeys.key1 + ' + '
        if(this.payload.hotkeys.key2) keys += this.payload.hotkeys.key2 + ' + '
        if(this.payload.hotkeys.key3) keys += this.payload.hotkeys.key3 + ' + '
        if(this.payload.hotkeys.key4) keys += this.payload.hotkeys.key4 + ' + '
        if(this.payload.hotkeys.key5) keys += this.payload.hotkeys.key5 + ' + '
        return keys
      }
    }
  },
  methods: {
    async saveChanges() {
      const hotkeys = []
          for(let i = 0; i < this.newCommandKeys.pressedString.length; i++) {
            const key = {}
            key['key' + (i + 1)] = {
                key: this.newCommandKeys.pressedString[i],
                location:i
              }
            hotkeys.push(key)
          }
      const payloadChanged = {
        name: this.payload.name,
        command_string: this.payload.command_string,
        hotkeys: hotkeys
      }
      await axios.patch('key/' + this.keyid + '/command/' + this.payload.id, payloadChanged)
    },
    async deleteCommand() {
      await axios.delete('key/' + this.keyid + '/command/' + this.payload.id)
      this.$emit('folder-changed')
    },
    keydown(event) {
      if(this.newCommandKeys.finished) {
        this.newCommandKeys.first = event.keyCode
        this.newCommandKeys.finished = false
        this.newCommandKeys.pressed = [event.keyCode]
        this.newCommandKeys.pressedString = [event.key]
      } else if (!this.newCommandKeys.pressed.includes(event.keyCode)) {
        this.newCommandKeys.pressed.push(event.keyCode)
        this.newCommandKeys.pressedString.push(event.key)
      }
    },
    keyup(event) {
      if(this.newCommandKeys.finished === false && event.keyCode === this.newCommandKeys.first) {
        this.newCommandKeys.finished = true
        this.newCommandKeybind = ''
      }
    }
  }
}
</script>