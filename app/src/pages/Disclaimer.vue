<template>
  <Page>
    <Section id="genturis-section-disclaimer" aria-labelledyby="genturis-section-disclaimer-title">
      <h2 id="genturis-section-disclaimer-title">Disclaimer</h2>
      <p>The GENTURIS registry was funded by the European Union’s Health Programme (2014-2020). The content of this website represents the views of the GENTURIS registry only and is it sole responsibility; it cannot be considered to reflect the views of the European Commission and/or the Consumers, Health, Agriculture and Food Executive Agency (CHAFEA) or any other body of the European Union. The European Commission and the Agency do not accept any responsibility for use that may be made of the information it contains.</p>
    </Section>
  </Page>
</template>

<script>
import Page from '../components/Page.vue'
import Section from '../components/Section.vue'

export default {
  name: 'page-privacy-policy',
  components: {
    Page,
    Section
  }
}
</script>
