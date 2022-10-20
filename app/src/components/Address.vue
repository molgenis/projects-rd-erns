<template>
  <address :class="setClassNames">
    <span><strong>Radboud University Medical Center</strong></span>
    <span>GENTURIS Registry</span>
    <span>Department of Human Genetics</span>
    <span>Geert Grooteplein Zuid 10</span>
    <span>6525 GA Nijmegen</span>
    <span>The Netherlands</span>
  </address>
</template>

<script>
export default {
  name: 'ern-address',
  props: {
    centerText: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    setClassNames () {
      const baseClass = 'address'
      const centeredTextClass = this.centerText ? 'address-text-center' : ''
      return [baseClass, centeredTextClass].join(' ')
    }
  }
}
</script>

<style lang="scss" scoped>
.address {
  font-size: 14pt;
  margin-left: 2.25em;
  span {
    display: block;
  }
  
  &.address-text-center {
    text-align: center;
  }
}
</style>
