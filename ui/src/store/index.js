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
    selectKey: (state, key) => state.selected = key,
    activeDeck: (state, deck) => {
      state.activeDeck = deck
      localStorage.setItem('activeDeck', deck)
    }
  },
  actions: {
    async initialize() {
      await Promise.all([
        this.dispatch('refreshDecks'),
      ])
      if(this.state.decks.length > 0)
        this.commit('set', ['activeDeck', this.state.decks[0].id])
        const browserSelectedDeck = localStorage.getItem('activeDeck')
      if(browserSelectedDeck) {
        const parsedBrowserSelectedDeck = parseInt(browserSelectedDeck)
        console.log('parsed ' + parsedBrowserSelectedDeck)
        this.commit('set', ['activeDeck', parsedBrowserSelectedDeck])
      }
    },
    async refreshDecks() {
      const decks = await axios.get('streamdecks')
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
      const decks = await axios.get('folders')
      this.commit('set', ['folders', decks.data])
    }
  },
  modules: {
  },
  getters: {
    selected: state => state.selected,
    activeDeck: state => {
      return state.decks.find(deck => deck.id === state.activeDeck)
    },
    activeDeckDefaultFolder: state => {
      return (state.decks.find(deck => deck.id === state.activeDeck)).default_folder.id
    },
    deckRows: (state, getters) => getters.activeDeck.streamdeck_model.key_count / getters.activeDeck.streamdeck_model.keys_per_row, 
    deckColumns: (state, getters) => getters.activeDeck.streamdeck_model.keys_per_row,
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
