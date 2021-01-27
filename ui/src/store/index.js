import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    models: [],
    decks: [],
    commands: [],
    keys: [],
    folders: [],
    activeDeck: -1, // TODO: Save in backend or localstorage?
    activeFolder: 1,
    selected: 1
  },
  mutations: {
    set: (state, [variable, value]) => {
      Vue.set(state, variable, value)
    },
    selectKey: (state, key) => state.selected = key
  },
  actions: {
    async initialize() {
      await Promise.all([
        this.dispatch('refreshModels'),
        this.dispatch('refreshDecks'),
        this.dispatch('refreshCommands'),
        this.dispatch('refreshKeys'),
        this.dispatch('refreshFolders')
      ])
      if(this.state.decks.length > 0)
        this.commit('set', ['activeDeck', this.state.decks[0].id])
    },
    async refreshModels() {
      const models = await axios.get('http://localhost:8000/streamdeckmodel/')
      this.commit('set', ['models', models.data])
    },
    async refreshDecks() {
      const decks = await axios.get('http://localhost:8000/streamdeck/')
      this.commit('set', ['decks', decks.data])
    },
    async refreshCommands() {
      const decks = await axios.get('http://localhost:8000/command/')
      this.commit('set', ['commands', decks.data])
    },
    async refreshKeys() {
      const decks = await axios.get('http://localhost:8000/streamdeckkeys/')
      this.commit('set', ['keys', decks.data])
    },
    async refreshFolders() {
      const decks = await axios.get('http://localhost:8000/folders/')
      this.commit('set', ['folders', decks.data])
    }
  },
  modules: {
  },
  getters: {
    selected: state => state.selected,
    selectedModel: state => {
      const active = state.decks.find(deck => deck.id === state.activeDeck)
      if(!active) return null
      const model = state.models.find(model => model.url === active.streamdeck_model)
      return model.length === 0 ? null : model
    },
    deckRows: (state, getters) => getters.selectedModel.key_count / getters.selectedModel.keys_per_row, 
    deckColumns: (state, getters) => getters.selectedModel.keys_per_row,
    selectedCommands: state => {
      const key = state.keys.find(key => key.id === state.selected)
      let command = state.commands.find(cmd => cmd.url === key.command)
      if(!command) return []
      const commands = []
      commands.push(command)
      while((command = command.following_command) !== null) {
        command = state.commands.find(cmd => cmd.url === command.url)
        commands.push(command)
      }
      return commands
    }
  }
})
