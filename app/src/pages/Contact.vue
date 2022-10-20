<template>
  <Page>
    <Section id="genturis-contact" aria-labelledby="genturis-contact-title">
      <h2 id="genturis-section-contact-title">Contact</h2>
      <p>For further information, please contact the GENTURIS registry coordination team by email <a href="mailto:genturis-registry@radboudumc.nl">genturis-registry@radboudumc.nl</a> or at the following address.</p>
      <Address :centerText="true" />
    </Section>
  </Page>
</template>

<script>
import Page from '../components/Page.vue'
import Section from '../components/Section.vue'
import Address from '../components/Address.vue'

export default {
  name: 'page-privacy-policy',
  components: {
    Page,
    Section,
    Address
  }
}
</script>
