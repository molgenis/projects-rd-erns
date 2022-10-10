<template>
  <section class="dashboard-section">
    <slot></slot>
  </section>
</template>

<script>
export default {
  name: 'dashboard-section'
}
</script>

<style>
.dashboard-section {
  box-sizing: padding-box;
  background-color: #ffffff;
  padding: 1em;
  border-radius: 8px;
  box-shadow: 0 0 3px 2px hsla(0, 0%, 0%, 0.12);
}
</style>
