<template>
    <div class="d3-viz d3-pie-chart">
      <svg
        :id="chartId"
        width="100%"
        height="100%"
        preserveAspectRatio="xMinYMin"
        viewBox="0 0 250 250"
      ></svg>
    </div>
</template>

<script>
import * as d3 from 'd3'

export default {
  name: 'PieChart',
  props: {
    chartId: {
      type: String,
      required: true
    },
    chartData: {
      type: Object,
      required: true
    },
    title: String,
    chartHeight: {
      type: Number,
      default: 250
    },
    chartWidth: {
      type: Number,
      default: 250
    },
    chartMargins: {
      type: Number,
      default: 20
    },
    chartColors: {
      type: Array,
      default: () => ['#98abc5', '#8a89a6', '#7b6888', '#6b486b', '#a05d56']
    }
  },
  methods: {
    renderChart () {
      // The radius of the pieplot is half the width or half the height (smallest one). I subtract a bit of margin.
      const radius = Math.min(this.chartWidth, this.chartHeight) / 2 - this.chartMargins

      // append the svg object to the div called 'my_dataviz'
      const svg = d3.select(`#${this.$el.childNodes[0].id}`)
        .append('g')
        .attr('transform', `translate(${this.chartWidth / 2}, ${this.chartHeight / 2})`)

      // set the color scale
      const color = d3.scaleOrdinal()
        .range(this.chartColors)

      // Compute the position of each group on the pie:
      const pie = d3.pie()
        .value(d => d[1])
      const pieChartData = pie(Object.entries(this.chartData))
      
      const arcGenerator = d3.arc()
        .innerRadius(0)
        .outerRadius(radius)

      // Build the pie chart: Basically, each part of the pie is a path that we build using the arc function.
      svg
        .selectAll('pie-slices')
        .data(pieChartData)
        .join('path')
        .attr('d', arcGenerator)
        .attr('fill', d => color(d.data[1]))
        .attr('stroke', 'black')
        .style('stroke-width', '2px')
        .style('opacity', 0.7)
        
      svg.selectAll('pie-slices')
        .data(pieChartData)
        .join('text')
        .text(d => `${d.data[0]}: ${d.data[1]}%`)
        .attr('transform', d => `translate(${arcGenerator.centroid(d)})`)
        .style('text-anchor', 'middle')
        .style('font-size', 11)
    }
  },
  watch: {
    chartData () {
      this.renderChart()
    }
  }
}
</script>
