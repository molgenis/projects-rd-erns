<template>
  <div class="router-link-card">
    <router-link :to="to">{{label}}</router-link>
  </div>
</template>

<script>
export default {
  name: 'router-link-card',
  props: {
    to: {
      type: Object
    },
    label: {
      type: String
    }
  }
}
</script>

<style lang="scss" scoped>
.router-link-card {
  box-sizing: content-box;
  padding: 1.25em;
  background-color: $blue-900;
  border-radius: 6px;
  text-align: center;
  
  a {
    color: $gray-050;
  }
}
</style>
