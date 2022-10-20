<template>
  <Page>
    <Header
      id="genturis-documents"
      title="ERN Genturis"
      subtitle="Import Documents and relevant information"
      :imageSrc="require('@/assets/images-wesley-tingey-documents.jpg')"
    />
    <Section id="genturis-section-documents" aria-labelledby="genturis-section-documents-title">
      <h2 id="genturis-section-documents-title">Documents</h2>
      <p>Useful documents about the GENTURIS registry will be added in the near future.</p>
    </Section>
  </Page>
</template>

<script>
import Page from '../components/Page.vue'
import Header from '../components/Header.vue'
import Section from '../components/Section.vue'

export default {
  name: 'page-documents',
  components: {
    Page,
    Header,
    Section
  }
}
</script>
