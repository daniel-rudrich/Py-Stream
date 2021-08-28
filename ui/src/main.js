import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import axios from 'axios'

Vue.config.productionTip = false

import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import bFormSlider from 'vue-bootstrap-slider'
import 'bootstrap-slider/dist/css/bootstrap-slider.css'
import InputColorPicker from 'vue-native-color-picker'

Vue.use(BootstrapVue)
Vue.use(bFormSlider)
Vue.use(IconsPlugin)
Vue.use(InputColorPicker)

console.log(window.location.host)
if(window.location.host === 'localhost:8080')
  axios.defaults.baseURL = 'http://localhost:8000/api/'
else
  axios.defaults.baseURL = '/api/'

console.log(axios.defaults.baseURL)

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
