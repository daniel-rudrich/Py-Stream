<template>
  <div v-if="payload">
    <h4><img :src="image" style="height: 30px;">Button #{{ payload.id }}</h4>
    <br>
    <b-form-input v-model="payload.text" placeholder="Enter key text" maxlength="10"></b-form-input>
    <br>
    <b-form-checkbox
      v-model="payload.clock"
      :value="true"
      :unchecked-value="false"
    >
      Clock
    </b-form-checkbox>
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

    <b-modal id="add-command" title="Add command" @ok="addCommand()">
      <b-form-select v-model="newCommandType" :options="[
        {value: 'shell', text: '(ba)sh'},
        {value: 'hotkey', text: 'Hotkey'},
        {value: 'timer', text: 'Timer'},
        {value: 'stopwatch', text: 'Stopwatch'}
      ]"></b-form-select>
      <br>
      <br>
      <b-form-input v-model="newCommandName" placeholder="Enter command name (optional)"></b-form-input>
      <br>
      <b-form-input v-show="newCommandType === 'shell'" v-model="newCommandCommand" placeholder="Enter command"></b-form-input>
      <span v-show="newCommandType === 'hotkey'" >You can edit the hotkeys after adding the command.</span>
      <b-form-input v-show="newCommandType === 'timer'" v-model="newCommandTimer" type="number" placeholder="Seconds"></b-form-input>
      <br>
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
      newCommandType: 'shell',
      newCommandName: '',
      newCommandCommand: 'echo New',
      newCommandKeybind: '',
      newCommandTimer: 5,
    }
  },
  mounted() {
  },
  computed: {
    commands() {
      return this.payload.Commands
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
            text: this.payload.text,
            clock: this.payload.clock || false
        }))
        if(this.newImage !== null) {
          promises.push(this.uploadNewImage())
          this.resetNewImage()
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
        let newCmd = {command_type: this.newCommandType}
        newCmd.name = this.newCommandName
        newCmd.command_string = ''
        if(newCmd.command_type === 'shell') {
          newCmd.command_string = this.newCommandCommand
        } else if(newCmd.command_type === 'hotkey') {
          newCmd.hotkeys = [{"key1":{"key":"Control","location":1}},{"key2":{"key":"1","location":0}}]
        } else if(newCmd.command_type === 'timer') {
          newCmd.time_value = parseInt(this.newCommandTimer)
        }
        console.log(newCmd)
        await axios.put('key/' + this.payload.id + '/command', newCmd)
        this.$emit('folder-changed')
      },
  }
}
</script>
