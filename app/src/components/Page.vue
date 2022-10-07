<template>
  <div class="app-page">
    <slot></slot>
    <footer class="app-footer">
      <div class="footer-section footer-logos">
        <img
          :src="require('@/assets/genturis-logo.jpg')"
          alt="European Reference Network on genetic tumour risk syndromes"
          class="genturis-logo"
        />
        <img
          :src="require('@/assets/molgenis-logo-blue-small.png')"
          alt="molgenis open source data platform"
          class="molgenis_logo"
        />
      </div>
      <div class="footer-section footer-navigation">
        <p><strong>Links</strong></p>
        <ul class="navlinks">
          <li><router-link :to="{'name': 'about'}">About</router-link></li>
          <li><router-link :to="{'name': 'governance'}">Governance</router-link></li>
          <li><router-link :to="{'name': 'documents'}">Documents</router-link></li>
          <li><router-link :to="{'name': 'dashboard'}">Dashboard</router-link></li>
          <li><router-link :to="{'name': 'privacy'}">Privacy Policy</router-link></li>
          <li><router-link :to="{'name': 'members'}">Members Area (account required)</router-link></li>
        </ul>
      </div>
      <div class="footer-section molgenis-citation">
        <p>This database was created using <a href="https://www.molgenis.org/">MOLGENIS open source  software</a> {{ molgenisVersion }} (released on {{ molgenisBuildDate }}).</p>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'page-ui',
  data () {
    return {
      molgenisVersion: null,
      molgenisBuildDate: null
    }
  },
  methods: {
    async fetchData (url) {
      const response = await fetch(url)
      return response.json()
    },
    getAppContext () {
      Promise.all([
        this.fetchData('/app-ui-context')
      ]).then(response => {
        const data = response[0]
        this.molgenisVersion = data.version
        this.molgenisBuildDate = data.buildDate.split(' ')[0]
      })
    }
  },
  mounted () {
    this.getAppContext()
  }
}
</script>

<style lang="scss" scoped>
.app-footer {
  background-color: $gray-900;
  box-sizing: padding-box;
  padding: 2em;
  
  .footer-section {
    margin-bottom: 24px;
  }
  
  .footer-logos {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 18px;
  }

  .footer-navigation {
    strong {
      color: $gray-050;
    }

    .navlinks {
      list-style: none;
      padding: 0;
      margin: 0;
      
      li {
        a {
          color: $gray-050;
          text-transform: uppercase;
          font-size: 11pt;
          letter-spacing: 0.08em;
        }
      }
    }
  }
  .molgenis-citation {
    font-size: 10pt;
    font-style: italic;
    p {
      color: $gray-200;
      a {
        color: currentColor;
        text-decoration: underline;
      }
    }
  }

}
</style>
