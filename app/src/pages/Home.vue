<template>
  <Page>
    <Header
      id="genturis-header"
      title="ERN Genturis Registry"
      subtitle="Registry for Genetic Tumour Risk Syndromes"
      :imageSrc="require('@/assets/genturis-bkg-2.jpg')"
    />
    <Section
      id="genturis-section-welcome"
      aria-labelledby="genturis-section-welcome-title"
    >
      <h2 id="genturis-section-welcome-title">
        Welcome to the GENTURIS registry
      </h2>
      <p>The GENTURIS registry is the European registry for patients with one of the genetic tumour risk syndromes (genturis). The registry is affiliated to the European Reference Network for all patients with one of the genetic tumour risk syndromes (ERN GENTURIS).</p>
    </Section>
    <Section
      id="genturis-section-quicklinks"
      aria-labelledby="genturis-section-quicklinks-title"
    >
      <h2 id="genturis-section-quicklinks-title">
        Quick Links
      </h2>
      <router-link :to="{name: 'dashboard'}">
        Dashboard
      </router-link>
    </Section>
    <Section
      id="genturis-section-aims"
      aria-labelledby="genturis-section-aims-title"
    >
      <h2 id="genturis-section-aims-title">
        Aims of the GENTURIS Registry
      </h2>
      <p>The aim of the GENTURIS registry is to enable research that will provide insights into the natural disease history and care pathway by gathering data from a large number of genturis patients and providing regulated data access following a data access policy.</p>
      <p>The registry enables a new wave of research opportunities from translational to epidemiological studies to clinical trials, and will accelerate the generation of new knowledge on genetic tumour risk syndromes. Research to improve recognition, detection, counselling and treatment of patients and to reduce variation in clinical outcomes across patients.</p>
      <ul>
        <li>To provide a sustainable, user-friendly and interoperable web-based registry platform that facilitates standardised registration of data on patients with a genturis known at participating Full Member and Affiliated Partner Health Care Providers (HCPs) of the ERN GENTURIS as well as other HCPs.</li>
        <li>To facilitate <strong>sharing of data</strong> across Europe.</li>
        <li>To be a <strong>unique source of data</strong> of a large number of patients with a genturis or patients highly suspected of a genturis.</li>
        <li>To enable <strong>European research</strong> ranging from basic research to clinical trials on genturis.</li>
        <li>To accelerate the generation of <strong>new knowledge</strong> on genturis through collaborative research.</li>
      </ul>
    </Section>
    <Section
      id="genturis-section-contact"
      aria-labelledby="genturis-section-contact-title"
    >
      <h2 id="genturis-section-contact-title">
        Contact
      </h2>
      <p>For further information please contact the GENTURIS registry coordination team via:</p>
      <address>
        <span>Radboud university medical center</span>
        <span>GENTURIS registry</span>
        <span>Department of Human Genetics</span>
        <span>Geert Grooteplein zuid 10</span>
        <span>6525 GA Nijmegen</span>
        <span>The Netherlands</span>
        <a href="mailto:genturis-registry@radboudumc.nl">genturis-registry@radboudumc.nl</a>
      </address>
    </Section>
    <Section
      id="genturis-section-disclaimer"
      aria-labelledby="genturis-section-disclaimer-title"
    >
      <h2 id="genturis-section-disclaimer-title">
        Disclaimer
      </h2>
      <p>The GENTURIS registry was funded by the European Union’s Health Programme (2014-2020). The content of this website represents the views of the GENTURIS registry only and is it sole responsibility; it cannot be considered to reflect the views of the European Commission and/or the Consumers, Health, Agriculture and Food Executive Agency (CHAFEA) or any other body of the European Union. The European Commission and the Agency do not accept any responsibility for use that may be made of the information it contains.</p>
    </Section>
  </Page>
</template>

<script>
import Page from '../components/Page.vue'
import Header from '../components/Header.vue'
import Section from '../components/Section.vue'

export default {
  name: 'home-page',
  components: {
    Page,
    Header,
    Section
  }
}
</script>

<style lang="scss" scoped>
#genturis-section-welcome {
  background-color: $secondary;
}

#genturis-section-contact {
  background-color: $gray-000;
}
</style>
