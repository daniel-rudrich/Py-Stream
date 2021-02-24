<template>
  <div v-if="payload">
    <h4><img :src="image" style="height: 30px;">Button #{{ payload.id }}</h4>
    <br>
    <b-form-input v-model="payload.text" placeholder="Enter key text"></b-form-input>
    <br>
    <input type="file" accept="image/*" @change="changeNewImageEvent($event)" id="file-input">
    <a href="javascript:void(0)" @click="resetNewImage">Reset</a>
    <br>
    <img v-show="newImage !== null" :src="imagePreview" height="70px" width="70px">
    <br v-show="newImage !== null">
    <br>
    <b-button variant="success" @click="saveChanges">Save</b-button>
    <br>
    <h3>Commands</h3>
    <div v-for="command in commands" :key="command.id">
      <command :payload="command" :keyid="payload.id" v-on:folder-changed="$emit('folder-changed')"></command>
    </div>
    <br>
    <b-button variant="primary" v-b-modal.add-command>Add command</b-button>
    &nbsp;
    <b-button variant="primary" @click="addFolder" v-show="payload.change_to_folder === null">Add folder</b-button>
    <br>
    <br>
    {{ payload }}

    <br><br>
    {{ commands }}

    <b-modal id="add-command" title="Add command" @ok="addCommand()">
      <b-form-select v-model="newCommandType" :options="[{value: 'sh', text: '(ba)sh'}, {value: 'keybind', text: 'Keybind'}]"></b-form-select>
      <br>
      <br>
      <b-form-input v-model="newCommandName" placeholder="Enter command name"></b-form-input>
      <br>
      <b-form-input v-show="newCommandType === 'sh'" v-model="newCommandCommand" placeholder="Enter command"></b-form-input>
      <b-form-input v-show="newCommandType === 'keybind'" v-model="newCommandKeybind" placeholder="Press key" @keydown="keydown($event)" @keyup="keyup($event)"></b-form-input>
      <br>
      Keybind: {{ newCommandKeys.pressedString }}<br>
      Keycodes: {{ newCommandKeys.pressed }}
    </b-modal>
  </div>
</template>

<script>
import axios from 'axios'
import Command from '@/components/Command.vue'

export default {
  name: 'BtnSettings',
  props: [
      'payload'
  ],
  components: {
      Command
    
  },
  data() {
    return {
      newImage: null,
      newCommandType: 'sh',
      newCommandName: '',
      newCommandCommand: 'echo New',
      newCommandKeybind: '',
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
    commands() {
      const commands = []
      let next = this.payload.command
      //let prev
      while(next) {
        commands.push(next)
        //prev = next
        next = next.following_command
        //delete prev.following_command
      }
      return commands
    },
    imagePreview() {
      if(this.newImage === null) return ''
      return URL.createObjectURL(this.newImage)
    },
    image() {
      if(this.payload.image_source === null) return 'https://www.elgato.com/themes/custom/smalcode/key-creator/assets/image_pool/sd31/btn_custom_trigger_hotkey2.svg'
      return 'http://localhost:8000' + this.payload.image_source
    }
  },
  methods: {
      async saveChanges() {
        const promises = []
        promises.push(axios.patch('key/' + this.payload.id, {
            text: this.payload.text
        }))
        if(this.newImage !== null) {
          promises.push(this.uploadNewImage())
        }
        await Promise.all(promises)
        this.$emit('folder-changed')
      },
      uploadNewImage() {
        const form = new FormData()
        form.append('image_source', this.newImage)
        return axios.put('key/' + this.payload.id + '/image_upload', form, {header: {'Content-Type': 'image/png'}})
      },
      async addFolder() {
        await axios.put('key/' + this.payload.id + '/folder', {name: 'New folder'})
        this.$emit('folder-changed')
      },
      async changeNewImageEvent(event) {
        this.newImage = event.target.files[0]
      },
      resetNewImage() {
        this.newImage = null
      },
      async addCommand() {
        await axios.put('key/' + this.payload.id + '/command', {name: this.newCommandName, command_string: this.newCommandCommand})
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