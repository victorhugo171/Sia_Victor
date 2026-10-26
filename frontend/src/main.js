import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { monto } from './utils/monto'
import './assets/role-theme.css'
import './assets/tema-sigta.css'
import './assets/gestion-sia.css'
import { cargarReglas } from './utils/reglas.js'
import './utils/swal' // <-- INICIALIZACIÓN DE MODALES GLOBALES

async function iniciarAplicacion() {
  await cargarReglas()

  const app = createApp(App)
  app.directive('monto', monto)
  app.use(router)
  app.mount('#app')
}

iniciarAplicacion()
