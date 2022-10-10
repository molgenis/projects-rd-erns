<template>
  <div class="d3-viz d3-table">
    <table :id="tableId">
      <caption v-if="caption">{{caption}}</caption>
    </table>
  </div>
</template>

<script>
import { select, selectAll } from 'd3'
const d3 = { select, selectAll }

export default {
  name: 'DataTable',
  props: {
    tableId: {
      type: String,
      required: true
    },
    data: {
      type: Array,
      required: true
    },
    columnOrder: {
      type: Array,
      required: false
    },
    caption: {
      type: String,
      required: false,
      default: null
    },
    visuallyHideHeader: {
      type: Boolean,
      required: false,
      default: false
    }
  },
  methods: {
    dataTypeToCssClass (cell) {
      let css = `column-${cell.column} data-value`
      const type = typeof cell.value
      css += ` value-${type}`
      if (type === 'number') {
        if (cell.value > 0) {
          css += ' value-positive'
        } else if (cell.value < 0) {
          css += ' value-negative'
        } else {
          css += ' value-zero'
        }
      }
      return css
    },
    renderTable () {
      const tableId = this.$el.childNodes[0].id
      const table = d3.select(`#${tableId}`)
      
      const tableHeader = table.append('thead')
        .attr('class', () => this.visuallyHideHeader ? 'visually-hidden-header' : '')
      tableHeader.append('tr')
        .selectAll('th')
        .data(this.columnOrder)
        .enter()
        .append('th')
        .attr('data-column-index', (column, index) => index)
        .attr('data-column-name', column => column)
        .text(column => column)

      const tableBody = table.append('tbody')
      const tableRows = tableBody.selectAll('tr')
        .data(this.data)
        .enter()
        .append('tr')

      const tableCells = tableRows.selectAll('tr')
        .data(row => {
          return this.columnOrder.map(column => {
            return { column: column, value: row[column] }
          })
        })
        .enter()
        .append('td')
        .attr('data-value', cell => cell.value)
        .text(cell => cell.value)

      tableCells.attr('class', cell => this.dataTypeToCssClass(cell))
    }
  },
  mounted () {
    this.renderTable()
  }
}
</script>

<style lang="scss">

$text-dark: #252525;
$text-default: #3f454b;

.d3-table {
  width: 100%;
  text-align: left;
  color: $text-default;

  table {
    border-spacing: 0;
    width: 100%;
    position: relative;
    
    caption {
      caption-side: top;
      font-size: 13pt;
      margin-bottom: 12px;
      font-weight: 600;
      color: $text-dark;
    }
    
    thead {
      tr {
        th {
          font-weight: 600;
          padding: 4px 12px;
          text-transform: uppercase;
          letter-spacing: 2px;
          border-bottom: 1px solid $text-dark;
          color: $text-dark;
        }
      }
      
      &.visually-hidden-header {
        position: absolute;
        clip: rect(1px 1px 1px 1px); /* IE6, IE7 */
        clip: rect(1px, 1px, 1px, 1px);
        overflow: hidden;
        height: 1px;
        width: 1px;
        margin: -1px;
        white-space: nowrap;
      }
    }
    
    tbody {
      tr {
        td {
          padding: 16px 12px;
          
          &.value-number {
            text-align: right;
          }
        }

        &:nth-child(even) {
          background-color: #f6f6f6;
        }
      }
    }
  }
}
</style>
