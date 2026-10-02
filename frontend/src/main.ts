/**
 * main.ts
 *
 * Bootstraps Vuetify and other plugins then mounts the App`
 */
import axios from 'axios'

axios.defaults.baseURL = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

// Plugins
import { registerPlugins } from '@/plugins'

// Components
import App from './App.vue'

// Composables
import { createApp } from 'vue'

// Styles
import 'unfonts.css'

const app = createApp(App)

registerPlugins(app)

app.mount('#app')
