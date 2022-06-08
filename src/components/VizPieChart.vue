<template>
    <div class="d3-viz d3-pie-chart">
      <svg :id="chartId" preserveAspectRatio="xMinYMin"></svg>
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
      default: 350
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
        .attr('width', this.chartWidth)
        .attr('height', this.chartHeight)
        .attr('viewbox', `0 0 ${this.chartWidth} ${this.chartHeight}`)
        .append('g')
        .attr('class', 'pie-chart-content')
        .attr('transform', `translate(${this.chartWidth / 2}, ${this.chartHeight / 2})`)

      // set the color scale
      const color = d3.scaleOrdinal()
        .range(this.chartColors)

      // Compute the position of each group on the pie:
      const pie = d3.pie().sort(null).value(d => d[1])
      const pieChartData = pie(Object.entries(this.chartData))
      
      const arcGenerator = d3.arc()
        .innerRadius(0)
        .outerRadius(radius * 0.7)
        
      const labelArcGenerator = d3.arc()
        .innerRadius(radius * 0.8)
        .outerRadius(radius * 0.8)

      // Build the pie chart: Basically, each part of the pie is a path that we build using the arc function.
      svg.selectAll('slices')
        .data(pieChartData)
        .join('path')
        .attr('d', arcGenerator)
        .attr('class', 'slices')
        .attr('fill', d => color(d.data[1]))
        .attr('stroke', '#3f454b')
        .style('stroke-width', '1px')
        .style('opacity', 0.7)
        
      // draw lines between slices and labels
      svg.selectAll('slice-label-lines')
        .data(pieChartData)
        .join('polyline')
        .attr('class', 'slice-label-lines')
        .attr('stroke', '#3f454b')
        .attr('fill', 'none')
        .attr('stroke-width', '1px')
        .attr('points', d => {
          // centroid of slices
          const start = arcGenerator.centroid(d)

          // centroid of the outer circle, i.e. where the line will break
          const mid = labelArcGenerator.centroid(d)
          
          // label position (largely the same as mid)
          const end = labelArcGenerator.centroid(d)
          
          // calculate if angle is left of to the right
          const angle = d.startAngle + (d.endAngle - d.startAngle) / 2
          
          // set position to the left or right
          end[0] = radius * 0.95 * (angle < Math.PI ? 1 : -1)
          return [start, mid, end]
        })
        
      // add labels
      svg.selectAll('slice-labels')
        .data(pieChartData)
        .join('text')
        .text(d => `${d.data[0]}\n${d.data[1]}%`)
        .attr('class', 'slice-labels')
        .attr('transform', d => {
          const position = labelArcGenerator.centroid(d)
          const angle = d.startAngle + (d.endAngle - d.startAngle) / 2
          position[0] = radius * 0.99 * (angle < Math.PI ? 1 : -1)
          return `translate(${position})`
        })
        .style('text-anchor', d => {
          const angle = d.startAngle + (d.endAngle - d.startAngle) / 2
          return angle < Math.PI ? 'start' : 'end'
        })
        .style('font-size', '11pt')
    }
  },
  mounted () {
    this.renderChart()
  }
}
</script>

<styles lang="scss">
.d3-pie-chart {
  .pie-chart-content {
    .slice-labels {
      white-space: pre;
    }
  }
}
</styles>
