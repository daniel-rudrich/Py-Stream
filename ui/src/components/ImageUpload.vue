<template>
  <div id="file-drag-drop">
      <button id="upload-trigger-key" v-b-modal.add-image-key>Change image</button>
      <b-modal
        static="true"
        id="add-image-key"
        title="Add image"
        ok-title="Save"
        @ok="addImage()"
        @cancel="resetNewImage()"
        @show="addEventListener()"
      >
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
      </b-modal>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "ImageUpload",
  props: {
    keyid: {
      type: Number,
      default: null,
    },
  },
  data() {
    return {
      dragAndDropCapable: false,
      newImage: null,
    };
  },
  mounted() {},
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
      form.append("image_source", this.newImage);
      return axios.put("key/" + this.keyid + "/image_upload", form, {
        header: { "Content-Type": "image/png" },
      });
      }
    },
    async deleteDeckImage(){
      if (this.streamdeckid !== null) {
        await axios.delete('streamdecks/' + this.streamdeckid + '/image_delete')
        this.$emit("folder-changed")
      }
    }
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
#upload-trigger-key {
  width: 80px;
  height: 80px;
  position: absolute;
  transform: translate(-40px, -80px);
  z-index: 3;
  opacity: 0;
  border-radius: 10%;
  font-size: 18px;
}

#upload-trigger-key:hover {
  opacity: 0.5;
}
</style>