<template>
  <div v-if="payload">
    <b-row v-if="payload.command_type === 'shell'">
      <b-col>
        <b-button id="delete-button" variant="danger" size="sm" @click="deleteCommand">x</b-button>       
      </b-col>
      <b-col>
          <p class ="command-type">{{ payload.command_type }}</p>
      </b-col>
      <b-col cols="2">
        <div class="command-col">
        <label>Command name</label>
        <b-form-input v-model="payload.name" placeholder="Command name"></b-form-input>
        </div>
      </b-col>
      <b-col  cols="2">
        <div class="command-col">
        <label>Command string</label>
        <b-form-input v-model="payload.command_string" placeholder="Command"></b-form-input>
        </div>
      </b-col>
      <b-col  cols="2">
        <div class="command-col">
        <label>Execution path</label>
        <b-form-input v-model="payload.active_directory" placeholder="."></b-form-input>
        </div>
      </b-col>
      <b-col  cols="2">
        <div class="command-col">
        <label>Timer value</label>
        <b-form-input v-model="payload.time_value" placeholder="Seconds"></b-form-input>
        </div>
      </b-col>
      <b-col>
        <b-button variant="success" size="sm" @click="saveChanges">Save</b-button>
      </b-col>
    </b-row>
    <b-row v-if="payload.command_type === 'hotkey'">
      <b-col>
        <b-button id="delete-button" variant="danger" size="sm" @click="deleteCommand">x</b-button>       
      </b-col>
      <b-col>
        <p class ="command-type">{{ payload.command_type }}</p>
      </b-col>
      <b-col cols="4">
        <div class="command-col">
        <label >Command Name</label>
        <b-form-input v-model="payload.name" placeholder="Command name"></b-form-input>
        </div>
      </b-col>
      <b-col  cols="4">
        <b-button :variant="listeningButtonColor" size="sm" @click="keyListenerBtn">{{ keys }}</b-button>
      </b-col>
      <b-col>
        <b-button variant="success" size="sm" @click="saveChanges">Save</b-button>
      </b-col>
    </b-row>
    <b-row v-if="payload.command_type === 'timer'">
      <b-col>
        <b-button id="delete-button" variant="danger" size="sm" @click="deleteCommand">x</b-button>       
      </b-col>
      <b-col>
        <p class ="command-type">{{ payload.command_type }}</p>
      </b-col>
      <b-col cols="4">
        <div class="command-col">
        <label >Command Name</label>
        <b-form-input v-model="payload.name" placeholder="Command name"></b-form-input>
        </div>
      </b-col>
      <b-col  cols="4">
        <div class="command-col">
        <label>Time value</label>
        <b-form-input v-model="payload.time_value" placeholder="Seconds"></b-form-input>
        </div>
      </b-col>
      <b-col>
        <b-button variant="success" size="sm" @click="saveChanges">Save</b-button>
      </b-col>
    </b-row>
    <b-row v-if="payload.command_type === 'stopwatch'">
      <b-col>
        <b-button id="delete-button" variant="danger" size="sm" @click="deleteCommand">x</b-button>       
      </b-col>
      <b-col>
        <p class ="command-type">{{ payload.command_type }}</p>
      </b-col>
      <b-col cols="4">
        <div class="command-col">
        <label>Command Name</label>
        <b-form-input v-model="payload.name" placeholder="Command name"></b-form-input>
        </div>
      </b-col>
      <b-col  cols="4">
        <p class="command-type">---</p>
      </b-col>
      <b-col>
        <b-button variant="success" size="sm" @click="saveChanges">Save</b-button>
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
      listening: false,
      newCommandKeys: {
        finished: true,
        pressed: [],
        pressedString: [],
        pressedLocation: [],
        first: null,
      }
    }
  },
  mounted() {
    
  },
  computed: {
    keys() {
      if(this.newCommandKeys.pressedString.length > 0) {
        return this.newCommandKeys.pressedString.join(' + ')
      } else {
        let keys = ''
        if(this.payload.hotkeys.key1) keys += this.payload.hotkeys.key1
        if(this.payload.hotkeys.key2) keys += ' + ' + this.payload.hotkeys.key2
        if(this.payload.hotkeys.key3) keys += ' + ' + this.payload.hotkeys.key3
        if(this.payload.hotkeys.key4) keys += ' + ' + this.payload.hotkeys.key4
        if(this.payload.hotkeys.key5) keys += ' + ' + this.payload.hotkeys.key5
        return keys
      }
    },
    listeningButtonColor() {
      return this.listening ? 'warning' : 'secondary'
    }
  },
  methods: {
    async saveChanges() {
      const hotkeys = []
          for(let i = 0; i < this.newCommandKeys.pressedString.length; i++) {
            const key = {}
            key['key' + (i + 1)] = {
                key: this.newCommandKeys.pressedString[i],
                location: this.newCommandKeys.pressedLocation[i]
              }
            hotkeys.push(key)
          }
      const payloadChanged = {
        name: this.payload.name,
        command_string: this.payload.command_string,
        time_value: this.payload.time_value,
        active_directory: this.payload.active_directory,
        hotkeys: hotkeys
      }
      await axios.patch('key/' + this.keyid + '/command/' + this.payload.id, payloadChanged)
      this.newCommandKeys.pressed = []
      this.newCommandKeys.pressedString = []
      this.$emit('folder-changed')
    },
    async deleteCommand() {
      await axios.delete('key/' + this.keyid + '/command/' + this.payload.id)
      this.$emit('folder-changed')
    },
    keyListenerBtn() {
      if(!this.listening) {
        window.addEventListener('keydown', this.keydown)
        window.addEventListener('keyup', this.keyup)
        this.listening = true
      } else {
        window.removeEventListener('keydown', this.keydown)
        window.removeEventListener('keyup', this.keyup)
        this.listening = false
      }
    },
    keydown(event) {
      if(this.newCommandKeys.finished) {
        this.newCommandKeys.first = event.keyCode
        this.newCommandKeys.finished = false
        this.newCommandKeys.pressed = [event.keyCode]
        this.newCommandKeys.pressedString = [event.key]
        this.newCommandKeys.pressedLocation = [event.location]
      } else if (!this.newCommandKeys.pressed.includes(event.keyCode)) {
        this.newCommandKeys.pressed.push(event.keyCode)
        this.newCommandKeys.pressedString.push(event.key)
        this.newCommandKeys.pressedLocation.push(event.location)
      }
    },
    keyup(event) {
      if(this.newCommandKeys.finished === false && event.keyCode === this.newCommandKeys.first) {
        this.newCommandKeys.finished = true
        this.newCommandKeybind = ''
        this.keyListenerBtn()
      }
    },




    changeHotkey() {

    }
  }
}
</script>
<style scoped>
  #delete-button{
    border-radius: 50%;
    border: 1px solid white;
    height: 28px;
    width: 28px;
    font-size: 16px;
    padding: 0;
    margin-top: auto;
    margin-bottom: auto;
  }
  .col{
    margin-top: auto;
    margin-bottom: auto;
  }
  .command-type{
    margin-top: 0;
    margin-bottom: 0;
  }
  .command-col{
    text-align: left;
  }
</style>