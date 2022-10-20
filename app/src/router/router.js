import { createRouter, createWebHistory } from 'vue-router'
import Home from '../pages/Home.vue'
import About from '../pages/About.vue'
import Governance from '../pages/Governance.vue'
import Documents from '../pages/Documents.vue'
import Dashboard from '../pages/Dashboard.vue'
import PrivacyPolicy from '../pages/Privacy.vue'
import MembersArea from '../pages/MembersArea.vue'
import Disclaimer from '../pages/Disclaimer.vue'
import Contact from '../pages/Contact.vue'

const initialState = window.__INITIAL_STATE__ || {}

const routes = [
  {
    name: 'home',
    path: '/',
    component: Home
  },
  {
    name: 'about',
    path: '/about',
    component: About
  },
  {
    name: 'contact',
    path: '/contact',
    component: Contact
  },
  {
    name: 'dashboard',
    path: '/dashboard',
    component: Dashboard
  },
  {
    name: 'disclaimer',
    path: '/disclaimer',
    component: Disclaimer
  },
  {
    name: 'documents',
    path: '/documents',
    component: Documents
  },
  {
    name: 'governance',
    path: '/governance',
    component: Governance
  },
  {
    name: 'members',
    path: '/members-area',
    component: MembersArea
  },
  {
    name: 'privacy',
    path: '/privacy',
    component: PrivacyPolicy
  }
]

const router = createRouter({
  history: createWebHistory(initialState.baseUrl),
  routes,
  scrollBehavior (to, from, savedPosition) {
    return {
      top: 0
    }
  }
})

export default router
