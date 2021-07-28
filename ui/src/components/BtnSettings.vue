<template>
  <div v-if="payload">
    <b-row>
      <b-col>
        <h4>
          <div class="container">
          <img :src="image" style="height: 100px; z-index: 1;">
          <button type="button" class="close" id="remove-image" aria-label="Close" @click="removeImage">
            <span aria-hidden="true">×</span>
          </button>
          <imageUpload 
            :keyid="payload.id" 
            v-on:folder-changed="$emit('folder-changed')">
          </imageUpload>
          </div>
        {{ payload.text }}
        </h4>
      </b-col>
    
    <!-- Text and clock key configuration-->
      <b-col>
        <b-form-input v-model="payload.text" v-on:change="waitToSave" placeholder="Enter key text" maxlength="10"/>
        <br>
        <b-form-checkbox
        v-model="payload.clock"
        :value="true"
        :unchecked-value="false"
        v-on:change="saveChanges"
        >
        Clock
        </b-form-checkbox>
        <br>
        <b-button variant="primary" @click="addFolder" v-show="payload.change_to_folder === null">Add folder</b-button>
        <b-button variant="primary" @click="deleteFolder" v-show="payload.change_to_folder != null">Delete folder</b-button>
      </b-col>
    </b-row>
    <h3>Commands</h3>
    <div v-for="command in commands" :key="command.id">
      <command :payload="command" :keyid="payload.id" v-on:folder-changed="$emit('folder-changed')"></command>
    </div>
    <br>

    <b-button variant="primary" v-b-modal.add-command>Add command</b-button>
    <br>
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
      <b-form-input v-show="newCommandType === 'shell'" v-model="newShellTimer" type="number" placeholder="Seconds"></b-form-input>
      <b-form-input v-show="newCommandType === 'shell'" v-model="newCommandDirectory" placeholder="."></b-form-input>
      <span v-show="newCommandType === 'hotkey'" >You can edit the hotkeys after adding the command.</span>
      <b-form-input v-show="newCommandType === 'timer'" v-model="newCommandTimer" type="number" placeholder="Seconds"></b-form-input>
      <br>
    </b-modal>

    
  </div>
</template>

<script>
import axios from 'axios'
import Command from '@/components/Command.vue'
import ImageUpload from '@/components/ImageUpload.vue'

export default {
  name: 'BtnSettings',
  props: [
      'payload'
  ],
  components: {
      Command,
      ImageUpload,
  },
  data() {
    return {
      timeout: null,
      waitTime: 1000,
      newImage: null,
      newCommandType: 'shell',
      newCommandName: '',
      newCommandCommand: 'echo New',
      newCommandKeybind: '',
      newCommandDirectory: '.',
      newCommandTimer: 5,
      newShellTimer: -1,
    }
  },
  mounted() {
  },
  computed: {
    commands() {
      return this.payload.Commands
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
            clock: this.payload.clock || false
        })
        this.$emit('folder-changed')
      },
      waitToSave(){
        // Unset previous timeout.
        clearTimeout(this.timeout);
        // Set current timeout.
        // If no further changes after 1 second, then save the change.
        this.timeout = setTimeout(function(){this.saveChanges()}.bind(this), this.waitTime);
      },
      async addFolder() {
        await axios.put('key/' + this.payload.id + '/folder', {name: 'New folder'})
        this.$emit('folder-changed')
      },
      async deleteFolder() {
        await axios.delete('key/' + this.payload.id + '/folder')
        this.$emit('folder-changed')
      },
      async changeNewImageEvent(event) {
        this.newImage = event.target.files[0]
      },
      async removeImage(){
        await axios.delete('key/' + this.payload.id)
        this.$emit('folder-changed')
      },
      async addCommand() {
        let newCmd = {command_type: this.newCommandType}
        newCmd.name = this.newCommandName
        newCmd.command_string = ''
        if(newCmd.command_type === 'shell') {
          newCmd.command_string = this.newCommandCommand
          newCmd.time_value = parseInt(this.newShellTimer)
          newCmd.active_directory = this.newCommandDirectory
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

<style>
  .form-control{
    color:white;
    background-color: #313131; 
    border: 1px solid black;
  }

  .form-control:focus{
    color:white;
    background-color: #313131;
  }
  .modal-title{
    color: white;
  }

  #remove-image{
    transform: translate(-19px, -11px);
    position: absolute;
    color: white;
    font-size: 25px;
    padding: 4px;
    height: 35px;
    width: 35px;
    border: 1px solid white;
    background: red;
    border-radius: 50%;
    z-index: 4;
  }
  
</style>