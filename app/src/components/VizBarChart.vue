<template>
  <div class="d3-viz d3-bar-chart">
    <svg :id="chartId" preserveAspectRatio="xMinYMin"></svg>
  </div>
</template>

<script>
import { select, selectAll, scaleBand, axisBottom, max, min, scaleLinear, axisLeft } from 'd3'
const d3 = { select, selectAll, scaleBand, axisBottom, max, min, scaleLinear, axisLeft }

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
    yMax: {
      type: Number
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
          bottom: 60,
          left: 60
        }
      }
    },
    barFill: {
      type: String,
      default: '#6C85B5'
    },
    barHoverFill: {
      type: String,
      default: '#163D89'
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
        .domain(this.chartData.map(row => row[this.xvar]))
        .padding(0.2)
      
      chartArea.append('g')
        .attr('transform', `translate(0, ${heightMarginAdjusted})`)
        .call(d3.axisBottom(xAxis))
        .selectAll('text')
        .style('text-anchor', 'middle')
        .style('font-size', '11pt')
        
      const ymax = this.yMax ? this.yMax : d3.max(this.chartData, row => row[this.yvar])
      const yAxis = d3.scaleLinear()
        .domain([0, ymax])
        .range([heightMarginAdjusted, 0])
        .nice()
      
      chartArea.append('g')
        .call(d3.axisLeft(yAxis))
        .selectAll('text')
        .style('font-size', '11pt')

      const chartColumns = chartArea.selectAll('columns')
        .data(this.chartData)
        .enter()
        .append('rect')
        .attr('class', 'chart-column')
        .attr('data-column', row => row[this.xvar])
        .attr('x', row => xAxis(row[this.xvar]))
        .attr('y', row => yAxis(row[this.yvar]))
        .attr('width', xAxis.bandwidth())
        .attr('height', row => heightMarginAdjusted - yAxis(row[this.yvar]))
        .attr('fill', this.barFill)
        
      chartArea.selectAll('column-labels')
        .data(this.chartData)
        .enter()
        .append('text')
        .attr('data-column', row => row[this.xvar])
        .attr('class', 'chart-column-labels')
        .attr('x', row => xAxis(row[this.xvar]))
        .attr('y', row => yAxis(row[this.yvar]))
        .attr('dx', xAxis.bandwidth() / 2)
        .attr('dy', '-3px')
        .attr('text-anchor', 'middle')
        .text(row => row[this.yvar])
        .style('opacity', '0')
        
      chartColumns.style('cursor', 'pointer')
        .on('mouseover', (event) => {
          const column = d3.select(event.target)
          const targetLabel = column.attr('data-column')
          const label = d3.select(`text[data-column="${targetLabel}"]`)
          column.attr('fill', this.barHoverFill)
          label.style('opacity', '1')
        })
        .on('mouseout', (event) => {
          const column = d3.select(event.target)
          const targetLabel = column.attr('data-column')
          const label = d3.select(`text[data-column="${targetLabel}"]`)
          column.attr('fill', this.barFill)
          label.style('opacity', '0')
        })
      
      svg.append('text')
        .attr('x', (this.chartWidth / 2) + (this.chartMargins.left * -0.35))
        .attr('y', this.chartHeight - (this.chartMargins.bottom / 4.5))
        .attr('text-anchor', 'middle')
        .style('font-size', '12pt')
        .text(this.xlabel)
      
      svg.append('text')
        .attr('class', 'chart-text chart-axis-title chart-axis-y')
        .attr('transform', 'rotate(-90)')
        .attr('transform-origin', 'top left')
        .attr('x', -(this.chartHeight / 2))
        .attr('y', this.chartMargins.left / 3)
        .attr('text-anchor', 'middle')
        .style('font-size', '12pt')
        .text(this.ylabel)
    }
  },
  mounted () {
    this.renderChart()
  }
}
</script>

<style lang="scss" scoped>
.d3-bar-chart {
  svg {
    display: block;
    margin: 0 auto;
  }
}
</style>
