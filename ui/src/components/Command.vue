<template>
  <div v-if="payload">
    <b-row>
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
    }
  },
  mounted() {
  },
  computed: {
    
  },
  methods: {
    async saveChanges() {
      await axios.patch('key/' + this.keyid + '/command/' + this.payload.id, {name: this.payload.name, command_string: this.payload.command_string})
    },
    async deleteCommand() {
      await axios.delete('key/' + this.keyid + '/command/' + this.payload.id)
      this.$emit('folder-changed')
    }
  }
}
</script>