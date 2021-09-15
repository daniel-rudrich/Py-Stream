<template>
  <div v-if="payload">
    <b-row>
      <b-col>
        <h4>
          <div class="container">
            <buttonImage :payload="payload"></buttonImage>
            <button type="button" class="close" id="remove-image" aria-label="Close" @click="removeImage">
              <span aria-hidden="true">×</span>
            </button>
            <imageUpload 
              :keyid="payload.id"
              v-on:folder-changed="$emit('folder-changed')">
            </imageUpload>
          </div>
        </h4>
        <p v-show="payload.change_to_folder != null">(folder)</p>
      </b-col>
    
    <!-- Text and clock key configuration-->
      <b-col>
        <b-row>
          <b-form-input v-model="payload.text" v-on:change="waitToSave" placeholder="Enter key text" maxlength="10"/>
        </b-row>
        <br>
        <b-row>
          <b-col>
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
          <b-col>
            <b-row>
              <b-col>
                <b-form-spinbutton id="sb-inline" v-model="payload.text_size" :min="1" :max="20" v-on:change="waitToSave"></b-form-spinbutton>
              </b-col>
              <b-col>
                <v-input-colorpicker  v-model="payload.text_color" v-on:change="saveChanges" style="height: 38px;"/>
              </b-col>
            </b-row>
            <br>
            <b-row>
              <b-col>
                <b-button-group size="sm" style="margin-right: 10px;">
                  <b-button class="text-button" v-bind:class="{'set-key': payload.text_bold}" @click="setTextStyle('bold')"><b>B</b></b-button>
                  <b-button class="text-button" v-bind:class="{'set-key': payload.text_italic}" @click="setTextStyle('italic')"><i>I</i></b-button>
                  <b-button class="text-button" v-bind:class="{'set-key': payload.text_underlined}" @click="setTextStyle('underlined')"><u>U</u></b-button>
               </b-button-group>
              </b-col>
              <b-col>
                <b-button-group size="sm">
                  <b-button class="text-button" v-bind:class="[payload.text_position === 'top' ? 'set-key':'']" @click="setTextPosition('top')"><b-icon icon="align-top"></b-icon></b-button>
                  <b-button class="text-button" v-bind:class="[payload.text_position === 'center' ? 'set-key':'']" @click="setTextPosition('center')"><b-icon icon="align-center"></b-icon></b-button>
                  <b-button class="text-button" v-bind:class="[payload.text_position === 'bottom' ? 'set-key':'']" @click="setTextPosition('bottom')"><b-icon icon="align-bottom"></b-icon></b-button>
                </b-button-group>
              </b-col>
            </b-row>
          </b-col>
        </b-row>
      </b-col>
    </b-row>
    <br>
    <br>
    <h3>
      Commands
      <b-button variant="primary" @click="runCommands" v-show="payload.Commands.length > 0">Run Commands</b-button>
    </h3>
    <div v-for="command in commands" :key="command.id">
      <command :payload="command" :keyid="payload.id" v-on:folder-changed="$emit('folder-changed')"></command>
      <br>
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
      <p>Command name:</p>
      <b-form-input v-model="newCommandName" placeholder="Enter command name (optional)"></b-form-input>
      <br>
      <p v-show="newCommandType === 'shell'">Command string</p>
      <b-form-input v-show="newCommandType === 'shell'" v-model="newCommandCommand" placeholder="Enter command"></b-form-input>
      <br v-show="newCommandType === 'shell'">
      <p v-show="newCommandType === 'shell'">Shell timer value; set -1 if command should not be executed in a time intervall (in seconds)</p>
      <b-form-input v-show="newCommandType === 'shell'" v-model="newShellTimer" type="number" placeholder="Seconds"></b-form-input>
      <br v-show="newCommandType === 'shell'">
      <p v-show="newCommandType === 'shell'">Execution path (directory)</p>
      <b-form-input v-show="newCommandType === 'shell'" v-model="newCommandDirectory" placeholder="."></b-form-input>
      <br v-show="newCommandType === 'shell'">
      <span v-show="newCommandType === 'hotkey'" color="white">You can edit the hotkeys after adding the command.</span>
      <br v-show="newCommandType === 'hotkey'">
      <p v-show="newCommandType === 'timer'">Timer value (in seconds)</p>
      <b-form-input v-show="newCommandType === 'timer'" v-model="newCommandTimer" type="number" placeholder="Seconds"></b-form-input>
      <br>
    </b-modal>

    
  </div>
</template>

<script>
import axios from 'axios'
import Command from '@/components/Command.vue'
import ImageUpload from '@/components/ImageUpload.vue'
import ButtonImage from './ButtonImage.vue'

export default {
  name: 'BtnSettings',
  props: [
      'payload'
  ],
  components: {
      Command,
      ImageUpload,
      ButtonImage
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
      original_image: null,
    }
  },
  computed: {
    commands() {
      return this.payload.Commands
    },
  },
  beforeUpdate() {
  },
  methods: {
      async saveChanges() {
        await axios.patch('key/' + this.payload.id, {
            text: this.payload.text,
            clock: this.payload.clock || false,
            text_size: this.payload.text_size,
            text_color: this.payload.text_color
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
      async setTextPosition(position){
        await axios.patch('key/' + this.payload.id, {text_position: position})
        this.$emit('folder-changed')
      },
      async setTextStyle(style){
        var bold = this.payload.text_bold
        var italic = this.payload.text_italic
        var underlined = this.payload.text_underlined

        if (style == "bold"){
          bold = !bold
        }
        if (style == "italic"){
          italic = !italic
        }
        if (style == "underlined"){
          underlined = !underlined
        }

        await axios.patch('key/' + this.payload.id, 
        {
          text_bold: bold, 
          text_italic: italic, 
          text_underlined: underlined
        })
        this.$emit('folder-changed')
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
      async runCommands(){
        await axios.get('key/' + this.payload.id + '/run_commands', {header: {'Content-Type': 'image/png'}})
        this.$emit('folder-changed')
      }
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
    transform: translate(20px, -90px);
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
  
  .text-button{
    background-color: #313131;
    border-color: black;
  }

  .text-button.set-key{
    background-color: #1f1e1e;
  }

  .modal-content{
    color: white;
  }

  .form-control.focus{
    background-color: #313131;
    color: white;
  }
</style>