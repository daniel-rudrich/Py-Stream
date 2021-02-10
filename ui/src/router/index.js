import Vue from 'vue'
import VueRouter from 'vue-router'
import Settings from '../views/Settings.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/settings',
    name: 'Settings',
    component: Settings
  },
  {
    path: '/',
    redirect: '/1' // TODO: Get this from Store
  },
  {
    path: '/:folder',
    name: 'Folder',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/Folder.vue')
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router