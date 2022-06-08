<template>
  <div class="d3-viz d3-bar-chart">
    <svg :id="chartId" preserveAspectRatio="xMinYMin"></svg>
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
    xvar: {
      type: String,
      require: true
    },
    yvar: {
      type: String,
      require: true
    },
    xAxisLabel: String,
    yAxisLabel: String,
    chartData: {
      type: Array,
      required: true
    },
    chartWidth: {
      type: Number,
      default: 675
    },
    chartHeight: {
      type: Number,
      default: 425
    },
    chartMargins: {
      type: Object,
      default () {
        return {
          top: 30,
          right: 30,
          bottom: 70,
          left: 60
        }
      }
    },
    barFill: {
      type: String,
      default: '#69b3a2'
    }
  },
  computed: {
    xlabel () {
      return this.xAxisLabel ? this.xAxisLabel : this.xvar
    },
    ylabel () {
      return this.yAxisLabel ? this.yAxisLabel : this.yvar
    }
  },
  methods: {
    renderChart () {
      const widthMarginAdjusted = this.chartWidth - this.chartMargins.left - this.chartMargins.right
      const heightMarginAdjusted = this.chartHeight - this.chartMargins.top - this.chartMargins.bottom
      
      const svg = d3.select(`#${this.$el.childNodes[0].id}`)
        .attr('width', this.chartWidth)
        .attr('height', this.chartHeight)
        .attr('viewbox', `0 0 ${this.chartWidth} ${this.chartHeight}`)
        
      const chartArea = svg.append('g')
        .attr('transform', `translate(${this.chartMargins.left}, ${this.chartMargins.top})`)
        
      const xAxis = d3.scaleBand()
        .range([0, widthMarginAdjusted])
        .domain(this.chartData.map(d => d[this.xvar]))
        .padding(0.2)
      
      chartArea.append('g')
        .attr('transform', `translate(0, ${heightMarginAdjusted})`)
        .call(d3.axisBottom(xAxis))
        .selectAll('text')
        .style('text-anchor', 'end')
        
      // properly calcuate ymax
      const ymax = d3.max(this.chartData, d => d[this.yvar])
      const yAxis = d3.scaleLinear()
        .domain([0, ymax])
        .range([heightMarginAdjusted, 0])
        .nice()
      
      chartArea.append('g').call(d3.axisLeft(yAxis))
      chartArea.selectAll('vertical-bars')
        .data(this.chartData)
        .enter()
        .append('rect')
        .attr('x', d => xAxis(d[this.xvar]))
        .attr('y', d => yAxis(d[this.yvar]))
        .attr('width', xAxis.bandwidth())
        .attr('height', d => heightMarginAdjusted - yAxis(d[this.yvar]))
        .attr('fill', this.barFill)
        
      if (this.xAxisTitle !== null) {
        svg.append('text')
          .attr('x', (this.chartWidth / 2) + (this.chartMargins.left * -0.35))
          .attr('y', this.chartHeight - (this.chartMargins.bottom / 2))
          .attr('text-anchor', 'middle')
          .style('font-size', '11pt')
          .text(this.xlabel)
      }
      
      if (this.yAxisTitle !== 'null') {
        svg.append('text')
          .attr('class', 'chart-text chart-axis-title chart-axis-y')
          .attr('transform', 'rotate(-90)')
          .attr('transform-origin', 'top left')
          // .attr('x', (this.chartMargins.left / 2))
          // .attr('y', (this.chartHeight / 2) + (this.chartMargins.top * -0.6))
          // .attr('x', (this.chartHeight / 2) + (this.chartMargins.top * -0.6))
          .attr('x', -(this.chartHeight / 2))
          .attr('y', this.chartMargins.left / 2)
          .attr('text-anchor', 'middle')
          .style('font-size', '11pt')
          .text(this.ylabel)
      }
    }
  },
  mounted () {
    this.renderChart()
  }
}
</script>
