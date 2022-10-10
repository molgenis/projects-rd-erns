<template>
  <ul class="legend">
    <li class="legend-item" data-legend-item="item" v-for="(label, index) in labels" :key="label">
      <svg class="item-marker" width="16" height="16" viewBox="0 0 16 16" preserveXminYmin="true">
        <circle cx="8" cy="8" r="8" :fill="colors[index]" stroke-width="none"></circle>
      </svg>
      <span class="item-label">{{ label }}</span>
    </li>
  </ul>
</template>

<script>
export default {
  props: {
    labels: {
      type: Array,
      required: true
    },
    colors: {
      type: Array,
      required: true
    }
  }
}
</script>

<style lang="scss" scoped>
.legend {
  list-style: none;
  padding: 0;
  margin: 0;
  
  .legend-item {
    display: block;
    
    .item-marker {
      display: inline-block;
      margin-right: 4px;
    }
    
    .item-label {
      display: inline-block;
      line-height: 1.4;
    }
}
  
}
</style>
