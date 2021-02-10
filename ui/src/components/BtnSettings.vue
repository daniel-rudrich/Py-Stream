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
    <br>
    <br>
    <b-button variant="success" @click="saveChanges">Save</b-button>
    <br>
    <h3>Commands</h3>
    <div v-for="command in commands" :key="command.id">
      <command :payload="command" :keyid="payload.id"></command>
    </div>
    <br>
    <b-button variant="primary" @click="saveChanges">Add command</b-button>
    <br>
    <b-button variant="primary" @click="addFolder" v-show="payload.change_to_folder === null">Add folder</b-button>
    <br>
    <br>
    {{ payload }}
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
      newImage: null
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
        await this.$store.dispatch('refreshDecks')
      },
      uploadNewImage() {
        const form = new FormData()
        form.append('name', 'image_source')
        form.append('file', this.newImage)
        return axios.put('key/' + this.payload.id + '/image_upload', form, {header: {'Content-Type': 'image/png'}})
      },
      async addFolder() {
        await axios.put('key/' + this.payload.id + '/folder', {name: 'New folder'})
        await this.$store.dispatch('refreshDecks')
      },
      async changeNewImageEvent(event) {
        this.newImage = event.target.files[0]
      },
      resetNewImage() {
        this.newImage = null
      },
  }
}
</script>