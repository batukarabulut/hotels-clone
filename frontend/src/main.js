// frontend/src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

// Bootstrap CSS
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

// Leaflet CSS for map functionality
import 'leaflet/dist/leaflet.css'

const app = createApp(App)

app.use(store)
app.use(router)

// Global error handler
app.config.errorHandler = (err, vm, info) => {
  console.error('Vue error:', err, info)
}

app.mount('#app')