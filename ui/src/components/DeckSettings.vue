<template>
    <div>
      <b-button variant="primary" id="upload-trigger-deck" v-b-modal.deck-settings><b-icon icon="pencil-square"></b-icon></b-button>
      <b-modal
        static="true"
        id="deck-settings"
        title="Streamdeck Settings"
        ok-title="Save"
        @ok="saveSettings()"
        @cancel="resetDeckImage()"
      >
        <p>Stream Deck Name</p>
        <b-form-input v-model="deckname" placeholder="Enter name"></b-form-input>
        <br>
        <p>Screensaver time</p>
        <b-form-input v-model="screensaverTime" min="1" max="86400" placeholder="Enter Screensaver Time"></b-form-input>
        <br>
        <p>Set Screensaver image</p>
        <div class="image-upload">
          <input type="file" id="file" ref="screensaver" v-on:change="handleScreensaverUpload()"/>
          <button v-on:click="resetScreensaverImage()">Clear</button>
          <button v-on:click="deleteScreensaverImage()">Default</button>
        </div>
        <br>
        <p>Set Full Deck Image</p>
        <div class="image-upload">
          <input type="file" id="file" ref="deckimage" v-on:change="handleDeckImageUpload()"/>
          <button v-on:click="resetDeckImage()">Clear</button>
          <button v-on:click="deleteDeckImage()">Remove</button>
        </div>
      </b-modal>
    </div>
</template>

<script>
import axios from "axios";

export default {
  name: "DeckSettings",
  props: {
    streamdeckid: {
      type: Number,
      default: null,
    },
  },
  data() {
    return {
      deckImage: null,
      screensaverImage: null,
      deckname: '',
      screensaverTime: 60,
    };
  },
  mounted() {
    const active = this.$store.getters.activeDeck
    this.deckname = active.name
    this.screensaverTime = active.screensaver_time
  },
  computed: {
  },
  methods: {
    handleScreensaverUpload(){
      this.screensaverImage = this.$refs.screensaver.files[0]
    },
    handleDeckImageUpload(){
      this.deckImage = this.$refs.deckimage.files[0]
    },
    resetDeckImage() {
      this.deckImage = null;
      this.$refs.deckimage.value = ''
    },
    resetScreensaverImage(){
      this.screensaverImage = null
      this.$refs.screensaver.value = ''
    },
    async saveSettings(){
        if(this.deckImage !== null){
          await this.uploadDeckImage()
          this.resetDeckImage()
        }
        if(this.screensaverImage !== null){
          await this.uploadScreensaverImage()
          this.resetScreensaverImage()
        }
        await axios.patch('streamdecks/' + this.streamdeckid, {
          name: this.deckname,
          screensaver_time: this.screensaverTime
        })
        await this.$store.dispatch('refreshDecks')
    },
    async uploadDeckImage() {
      const form = new FormData();
      if (this.streamdeckid !== null) {
        form.append("full_deck_image", this.deckImage);
        await axios.put(
          "streamdecks/" + this.streamdeckid + "/image_upload",
          form,
          { header: { "Content-Type": "image/png" } }
        );
      }
    },
    async uploadScreensaverImage() {
      const form = new FormData();
      if (this.streamdeckid !== null) {
        form.append("screensaver_image", this.screensaverImage);
        await axios.put(
          "streamdecks/" + this.streamdeckid + "/screensaver_image_upload",
          form,
          { header: { "Content-Type": "image/png" } }
        );
      }
    },
    async deleteDeckImage() {
      if (this.streamdeckid !== null) {
        await axios.delete(
          "streamdecks/" + this.streamdeckid + "/image_delete"
        );
        this.resetDeckImage()
        this.$emit("folder-changed");
      }
    },
    async deleteScreensaverImage(){
      if (this.streamdeckid !== null) {
        await axios.delete(
          "streamdecks/" + this.streamdeckid + "/screensaver_image_delete"
        );
        this.resetScreensaverImage()
      }
    }
  },
};
</script>

<style>
.image-upload {
  font-size: 15px;
}

.modal-content {
  background-color: #212121;
  border: 3px solid black;
  font-size: 1.5rem;
  text-align: left;
}
.modal-header {
  border-bottom: 2px solid black;
}
.modal-footer {
  border-top: 2px solid black;
}
.close {
  color: white;
  font-size: 2rem;
  text-shadow: none;
  opacity: 1;
}
.close:hover {
  color: #313131;
}
</style>