<template>
  <div
    :class="imageSrc ? 'router-link-card card-bg-image' : 'router-link-card'"
    :style="imageSrc ? `background-image: url(${imageSrc})` : ''"
  >
    <div class="card-content">
      <router-link :to="to">{{label}}</router-link>
    </div>
    <div class="card-bg-filter" v-if="imageSrc" aria-hidden="false" />
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
    },
    imageSrc: {
      type: String
    }
  }
}
</script>

<style lang="scss">
.router-link-card {
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  background-color: $gray-900-alt;
  padding: 24px;
  
  $card-sizing: 12em;
  width: $card-sizing;
  height: $card-sizing;
  
  .card-content {
    z-index: 1;
    a {
      color: $gray-050;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      font-weight: bold;
      font-size: 14pt;
    }
  }
  
  &.card-bg-image {
    background-size: cover;
    background-position: 0 44%;
    
    .card-bg-filter {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: $black-transparent-100;
    }
  }
}
</style>
