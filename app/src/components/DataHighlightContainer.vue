<template>
  <div :id="id" class="highlight-container">
    <slot></slot>
  </div>
</template>

<script>
export default {
  name: 'data-highlight-container',
  props: {
    id: {
      type: String,
      required: true
    }
  }
}
</script>

<style lang="scss" scoped>
.highlight-container {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 1.5em;
  box-sizing: padding-box;
}
</style>
