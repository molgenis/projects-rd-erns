<template>
  <div class="app-page">
    <slot></slot>
    <footer class="app-footer">
      <div class="footer-section footer-logos">
        <img
          :src="require('@/assets/molgenis-logo-blue-small.png')"
          alt="molgenis open source data platform"
          class="molgenis_logo"
        />
      </div>
      <div class="footer-section footer-navigation">
        <ul class="navlinks">
          <li><router-link :to="{'name': 'dashboard'}">Dashboard</router-link></li>
          <li><router-link :to="{'name': 'privacy'}">Privacy Policy</router-link></li>
        </ul>
      </div>
      <div class="footer-section molgenis-citation">
        <p><small>This database was created using the open source MOLGENIS software {{ molgenisVersion }} on {{ molgenisBuildDate }}</small></p>
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
        this.molgenisBuildDate = data.buildDate
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
    margin-bottom: 12px;
  }

  .footer-navigation {
    .navlinks {
      list-style: none;
      padding: 0;
      margin: 0;
      
      li {
        display: inline-block;
        margin-right: 18px;
        
        &:last-child {
          margin-right: 0;
        }
        
        a {
          color: $gray-050;
          text-transform: uppercase;
          font-size: 11pt;
          font-weight: bold;
        }
      }
    }
  }
  
  .molgenis-citation {
    color: $gray-200;
  }
}
</style>
