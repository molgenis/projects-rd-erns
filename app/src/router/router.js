import { createRouter, createWebHistory } from 'vue-router'
import Home from '../pages/Home.vue'
import About from '../pages/About.vue'
import Governance from '../pages/Governance.vue'
import Documents from '../pages/Documents.vue'
import Dashboard from '../pages/Dashboard.vue'
import PrivacyPolicy from '../pages/Privacy.vue'
import MembersArea from '../pages/MembersArea.vue'

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
    name: 'governance',
    path: '/governance',
    component: Governance
  },
  {
    name: 'documents',
    path: '/documents',
    component: Documents
  },
  {
    name: 'dashboard',
    path: '/dashboard',
    component: Dashboard
  },
  {
    name: 'privacy',
    path: '/privacy',
    component: PrivacyPolicy
  },
  {
    name: 'members',
    path: '/members-area',
    component: MembersArea
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
