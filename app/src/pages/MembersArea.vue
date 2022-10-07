<template>
  <Page>
    <header id="genturis-members-header">
      <h1>Health Care Providers</h1>
    </header>
    <Section id="genturis-section-members" aria-labelledby="genturis-section-members-title">
      <h2 id="genturis-section-members-title">Health Care Providers</h2>
      <p>This page is under construction.</p>
    </Section>
  </Page>
</template>

<script>
import Page from '../components/Page.vue'
import Section from '../components/Section.vue'

export default {
  name: 'page-documents',
  components: {
    Page,
    Section
  }
}
</script>

<style lang="scss" scoped>
#genturis-members-header {
  background-color: $gray-000;
  box-sizing: content-box;
  padding: 2em;
}
</style>
