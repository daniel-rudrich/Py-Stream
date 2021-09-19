<template>
    <div>
      <b-button variant="primary" id="upload-trigger-deck" v-b-modal.deck-settings><b-icon icon="pencil-square"></b-icon></b-button>
      <b-modal
        static="true"
        id="deck-settings"
        title="Streamdeck Settings"
        ok-title="Save"
        @ok="saveSettings()"
        @cancel="resetNewImage()"
        @show="addEventListener()"
      >
        <p>Stream Deck Name</p>
        <b-form-input v-model="deckname" placeholder="Enter name"></b-form-input>
        <br>
        <p>Set Full Deck Image</p>
        <form ref="fileform" @click="$refs.file.click()">
          <input
            type="file"
            ref="file"
            accept="image/*"
            @change="changeNewImageEvent($event)"
            id="file-input"
            style="display: none"
          />
          <span class="drop-files"
            >Drop the image here! Or click to choose an image from your file
            browser!</span
          >
        </form>
        <img
          v-show="newImage != null"
          :src="imagePreview"
          height="70px"
          width="70px"
        />
        <a v-if="newImage != null">{{ newImage.name }}</a>
        <template #modal-footer="{ ok, cancel }">
          <!-- Emulate built in modal footer ok and cancel button actions -->
          <b-button size="sm" variant="success" @click="ok()">
            OK
          </b-button>
          <b-button size="sm" variant="danger" @click="cancel()">
            Cancel
          </b-button>
          <!-- Button with custom close trigger value -->
          <b-button size="sm" variant="outline-secondary" @click="deleteDeckImage()">
            Delete Image
          </b-button>
        </template>
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
      dragAndDropCapable: false,
      newImage: null,
      deckname: '',
    };
  },
  mounted() {
    const active = this.$store.getters.activeDeck
    this.deckname = active.name
  },
  computed: {
    imagePreview() {
      if (this.newImage === null) return "";
      return URL.createObjectURL(this.newImage);
    },
  },
  methods: {
    determineDragAndDropCapable() {
      var div = document.createElement("div");

      return (
        ("draggable" in div || ("ondragstart" in div && "ondrop" in div)) &&
        "FormData" in window &&
        "FileReader" in window
      );
    },
    addEventListener() {
      this.dragAndDropCapable = this.determineDragAndDropCapable();

      if (this.dragAndDropCapable) {
        [
          "drag",
          "dragstart",
          "dragend",
          "dragover",
          "dragenter",
          "dragleave",
          "drop",
        ].forEach(
          function (evt) {
            this.$refs.fileform.addEventListener(
              evt,
              function (e) {
                e.preventDefault();
                e.stopPropagation();
              }.bind(this),
              false
            );
          }.bind(this)
        );

        this.$refs.fileform.addEventListener(
          "drop",
          function (e) {
            this.newImage = e.dataTransfer.files[0];
          }.bind(this)
        );
      }
    },
    async saveSettings(){
        if(this.newImage !== null){
            this.uploadNewImage()
        }
        await axios.patch('streamdecks/' + this.streamdeckid, {
          name: this.deckname,
        })
        await this.$store.dispatch('refreshDecks')
    },
    async changeNewImageEvent(event) {
      this.newImage = event.target.files[0];
    },
    resetNewImage() {
      this.newImage = null;
    },
    async addImage() {
      if (this.newImage !== null) {
        await this.uploadNewImage();
        this.resetNewImage();
      }
      this.$emit("folder-changed");
    },
    uploadNewImage() {
      const form = new FormData();
      if (this.streamdeckid !== null) {
        form.append("full_deck_image", this.newImage);
        return axios.put(
          "streamdecks/" + this.streamdeckid + "/image_upload",
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
        this.$emit("folder-changed");
      }
    },
  },
};
</script>

<style>
form {
  display: block;
  height: 400px;
  width: 400px;
  background: #212121;
  margin: auto;
  margin-top: 40px;
  text-align: center;
  border-radius: 4px;
  cursor: pointer;
}
form:hover {
  background-color: #313131;
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

.drop-files {
  height: 400px;
  display: flex;
  align-items: center;
  border: 3px solid black
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