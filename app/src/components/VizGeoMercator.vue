<template>
  <div class="d3-viz d3-geo-mercator" :style="waterColor ? `background-color: ${waterColor}` : ''">
    <svg :id="chartId"></svg>
    <div class="d3-viz-legend" v-if="legendLabels.length & legendColors.length">
      <chartLegend :labels="legendLabels" :colors="legendColors"/>
    </div>
  </div>
</template>

<script>
import chartLegend from './VizLegend.vue'
import { select, selectAll, geoMercator, geoPath, json } from 'd3'
const d3 = { select, selectAll, geoMercator, geoPath, json }

export default {
  props: {
    chartId: {
      type: String,
      required: true
    },
    geojson: {
      type: Object,
      required: true
    },
    chartData: {
      type: Array,
      required: true
    },
    fillVariable: {
      type: String
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
    },
    legendLabels: {
      type: Array
    },
    legendColors: {
      type: Array
    },
    showTooltip: {
      type: Boolean,
      default: true
    },
    landColor: {
      type: String,
      default: '#4E5327'
    },
    borderColor: {
      type: String,
      default: '#757D3B'
    },
    waterColor: {
      type: String,
      default: '#6C85B5'
    }
  },
  components: { chartLegend },
  data () {
    return {
      svg: null,
      tooltip: null
    }
  },
  methods: {
    initSvg () {
      this.svg = d3.select(`#${this.$el.childNodes[0].id}`)
        .attr('width', this.chartWidth)
        .attr('height', this.chartHeight)
        .attr('preserveAspectRatio', 'xMinYMin')
        .attr('viewbox', `0 0 ${this.chartSize} ${this.chartSize / 2}`)
    },
    removeTooltip () {
      d3.selectAll(`#${this.chartId}-tooltip`).remove()
    },
    createTooltip () {
      this.removeTooltip()
      this.tooltip = d3.select('body')
        .style('position', 'relative')
        .append('div')
        .style('position', 'absolute')
        .attr('id', `${this.chartId}-tooltip`)
        .attr('class', 'map-chart-tooltip')
        .style('opacity', 0)
    },
    onMouseOver () {
      this.tooltip.style('opacity', 1)
    },
    onMouseMove (event, data) {
      this.tooltip.html(`<p class="title">${data.displayName}</p><p>${data.city}, ${data.country}</p>`)
        .style('left', `${event.pageX + 8}px`)
        .style('top', `${event.pageY - 55}px`)
    },
    onMouseLeave () {
      this.tooltip.style('opacity', 0)
    },
    renderChart () {
      this.initSvg()

      const mapLayer = this.svg.append('g').attr('class', 'geojson-layer')

      const projection = d3.geoMercator()
        .center(this.chartCenterCoordinates)
        .scale(this.chartWidth * this.chartScale)
        .translate([this.chartWidth / 2, this.chartHeight / 2])
      
      const path = d3.geoPath().projection(projection)

      mapLayer.selectAll('path')
        .data(this.geojson.features)
        .enter()
        .append('path')
        .attr('fill', this.landColor)
        .attr('d', path)
        .attr('stroke', this.borderColor)
        
      const dataLayer = this.svg.append('g').attr('class', 'data-layer')
      const points = dataLayer.selectAll('circle')
        .data(this.chartData)
        .enter()
        .append('circle')
        .style('cursor', 'pointer')
        .attr('cx', row => projection([row.longitude, row.latitude])[0])
        .attr('cy', row => projection([row.longitude, row.latitude])[1])
        .attr('r', '5')
        .attr('fill', row => { return row[this.fillVariable] })
      
      if (this.showTooltip) {
        this.createTooltip()
        points.on('mouseover', this.onMouseOver)
          .on('mousemove', (event, row) => this.onMouseMove(event, row))
          .on('mouseleave', this.onMouseLeave)
      }
    }
  },
  mounted () {
    this.renderChart()
  }
}
</script>

<style lang="scss">
.d3-geo-mercator {
  position: relative;
  svg {
    display: block;
    margin: 0 auto;
  }
  
  .d3-viz-legend {
    position: absolute;
    top: 0;
    left: 0;
    color: $gray-050;
    border: 1px solid $gray-900;
    background-color: $gray-900;
    padding: 12px;
    box-shadow: 2px 4px 4px 2px hsla(0, 0%, 0%, 0.2)
  }
}

.map-chart-tooltip {
  max-width: 325px;
  z-index: 10;
  background-color: #ffffff;
  box-shadow: 0 0 4px 2px hsla(0, 0%, 0%, 0.2);
  border-radius: 3px;
  padding: 8px 12px;

  p {
    font-size: 10pt;
    padding: 0;
    margin: 0;
    
    &.title {
      font-size: 10pt;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      line-height: 1.2;
      font-weight: bold;
    }
  }
}
</style>
