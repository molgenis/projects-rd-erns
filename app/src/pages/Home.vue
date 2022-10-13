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
      <img
        :src="require('@/assets/genturis-logo-crab.jpg')"
        class="genturis-logo-crab"
        alt="genturis registry"
      />
      <h2 id="genturis-section-welcome-title">
        Welcome to the GENTURIS registry
      </h2>
      <p>The <strong>GENTURIS</strong> registry is the European registry for patients with one of the genetic tumour risk syndromes (genturis). The registry is affiliated to the European Reference Network for all patients with one of the genetic tumour risk syndromes (ERN GENTURIS).</p>
    </Section>
    <section class="quicklink-cards" aria-labelledby="quicklinks-card-title">
      <h2 class="visually-hidden" id="quicklinks-card-title">quick links</h2>
      <RouterLinkCard
        id="quicklinks-about"
        :to="{name: 'about'}"
        label="About Us"
      />
      <RouterLinkCard
        id="quicklink-documents"
        :to="{name: 'documents'}"
        label="Documents"
        :imageSrc="require('@/assets/images-wesley-tingey-documents.jpg')"
      />
      <RouterLinkCard
        id="quicklink-dashboard"
        :to="{name: 'dashboard'}"
        label="Dashboard"
        :imageSrc="require('@/assets/images-markus-winkler-dashboard.jpg')"
      />
    </section>
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
    <Section id="genturis-section-contact" aria-labelledby="genturis-section-contact-title">
      <h2 id="genturis-section-contact-title">Contact</h2>
      <p>For further information, please contact the GENTURIS registry coordination team by email <a href="mailto:genturis-registry@radboudumc.nl">genturis-registry@radboudumc.nl</a> or at the following address.</p>
      <Address :centerText="true" />
    </Section>
  </Page>
</template>

<script>
import Page from '../components/Page.vue'
import Header from '../components/Header.vue'
import Section from '../components/Section.vue'
import RouterLinkCard from '../components/RouterLinkCard.vue'
import Address from '../components/Address.vue'

export default {
  name: 'home-page',
  components: {
    Page,
    Header,
    Section,
    RouterLinkCard,
    Address
  }
}
</script>

<style lang="scss">

#genturis-header {
  justify-content: center;
  align-items: flex-end;
  
  .header-content {
    text-align: center;
  }
}

#genturis-section-welcome,
#genturis-section-contact {
  background-color: $gray-000;
}
#genturis-section-quicklinks {
  background-color: $brand-050;
}

.quicklink-cards {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: row;
  flex-wrap: wrap;
  
  .router-link-card {
    flex-grow: 1;
  }
}

#quicklinks-about {
  background-color: $blue-900;
}

#quicklink-documents {
  .card-bg-filter {
    background-color: $brand-900;
    opacity: 0.80;
  }
}

#quicklink-dashboard {
  .card-bg-filter {
    background-color: $blue-800;
    opacity: 0.65;
  }
}

</style>
