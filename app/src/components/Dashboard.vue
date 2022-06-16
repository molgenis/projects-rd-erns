<template>
  <div class="dashboard">
    <slot></slot>
  </div>
</template>

<script>
export default {
  name: 'DasboardUI'
}
</script>

<style lang="scss">
.dashboard {
  box-sizing: padding-box;
  padding: 2em 1em;
}
</style>
