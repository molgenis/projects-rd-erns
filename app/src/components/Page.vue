<template>
  <div class="app-page">
    <slot></slot>
    <PageFooter />
  </div>
</template>

<script>
import PageFooter from './PageFooter.vue'

export default {
  name: 'page-ui',
  components: { PageFooter }
}
</script>
