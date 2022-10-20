<template>
  <section>
    <div class="section-content">
      <slot></slot>
    </div>
  </section>
</template>

<script>
export default {
  name: 'ui-section'
}
</script>

<style lang="scss" scoped>
section {
  background-color: $gray-050;
  box-sizing: content;
  padding: 2em;
  
  .section-content {
    max-width: 972px;
    margin: 0 auto;
  }
}
</style>
