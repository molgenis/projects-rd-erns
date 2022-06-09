<template>
  <div class="d3-viz d3-geo-mercator">
    <svg :id="chartId"></svg>
  </div>
</template>

<script>
import * as d3 from 'd3'

export default {
  props: {
    chartId: {
      type: String,
      required: true
    },
    chartData: {
      type: Array,
      required: true
    },
    chartWidth: {
      type: Number,
      default: 500
    },
    chartHeight: {
      type: Number,
      default: 500
    },
    chartCenterCoordinates: {
      type: Array,
      default: () => [15, 53]
    },
    chartSize: {
      type: Number,
      default: 700
    },
    chartScale: {
      type: Number,
      default: 1.1
    }
  },
  data () {
    return {
      geojson: null
    }
  },
  methods: {
    renderChart () {
      const svg = d3.select(`#${this.$el.childNodes[0].id}`)
        .attr('width', '100%')
        .attr('height', this.chartHeight)
        .attr('preserveAspectRatio', 'xMinYMin')
        .attr('viewbox', `0 0 ${this.chartSize} ${this.chartSize / 2}`)
      
      const mapLayer = svg.append('g')
        .attr('class', 'geojson-layer')

      const projection = d3.geoMercator()
        .center(this.chartCenterCoordinates)
        .scale(this.chartWidth * this.chartScale)
        .translate([this.chartWidth / 2, this.chartHeight / 2])
      
      const path = d3.geoPath().projection(projection)
      mapLayer.selectAll('path')
        .data(this.geojson.features)
        .enter()
        .append('path')
        .attr('fill', '#d6d6d6')
        .attr('d', path)
        .attr('stroke', '#f6f6f6')
        
      const dataLayer = svg.append('g')
        .attr('class', 'data-layer')
        
      dataLayer.selectAll('circle')
        .data(this.chartData)
        .enter()
        .append('circle')
        .attr('cx', d => projection([d.longitude, d.latitude])[0])
        .attr('cy', d => projection([d.longitude, d.latitude])[1])
        .attr('r', '4')
        .attr('fill', d => d.hasSubmittedData ? '#3b3b3b' : '#94a6da')
    }
  },
  mounted () {
    d3.json('/europe.geojson').then(data => {
      this.geojson = data
    }).then(() => {
      this.renderChart()
    })
  }
}
</script>

<style lang="scss">
</style>
