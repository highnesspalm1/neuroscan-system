import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import Toast from 'vue-toastification'
import App from './App.vue'

// CSS imports
import './style.css'
import 'vue-toastification/dist/index.css'

// Toast configuration
const toastOptions = {
  position: "top-right",
  timeout: 5000,
  closeOnClick: true,
  pauseOnFocusLoss: true,
  pauseOnHover: true,
  draggable: true,
  draggablePercent: 0.6,
  showCloseButtonOnHover: false,
  hideProgressBar: false,
  closeButton: "button",
  icon: true,
  rtl: false,
  toastClassName: "glass-toast",
  bodyClassName: "toast-body",
  hideCloseButton: false,
}

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(Toast, toastOptions)

app.mount('#app')
