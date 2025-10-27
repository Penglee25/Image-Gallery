import { createApp } from 'vue'
import './style.css'
import './assets/css/custom.css'

import router from './router'

import App from './App.vue'

import AOS from 'aos'
import 'aos/dist/aos.css'

createApp(App)
.use(router)
.mount('#app')

AOS.init({ duration: 800, easing: 'slide', once: true });