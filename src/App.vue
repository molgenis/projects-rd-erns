<template>
    <div id="app">
      <header>
        <h1>Summary Statistics</h1>
      </header>
      <main class="container-fluid">
        <div class="row">
          <div class="col-sm-6">
            <p>[insert map here]</p>
          </div>
          <div class="col-sm-6">
            <div class="row">
              <div class="col-sm-6">
                <div class="row">
                  <DataTable
                    tableId="country_enrollment"
                    :data="country_enrollment.data"
                    :columnOrder='["label","value"]'
                    :caption="country_enrollment.title"
                  />
                </div>
                <div class="row">
                  <DataTable
                    tableId="hcp_enrollment"
                    :data="hcp_enrollment.data"
                    :columnOrder='["label", "value"]'
                    :caption="hcp_enrollment.title"
                  />
                </div>
              </div>
              <div class="col-sm-6">
                <h2>{{ sex_at_birth.title }}</h2>
                <PieChart
                  chartId="sex-at-birth"
                  :chartData="sex_at_birth.data"
                />
              </div>
            </div>
            <div class="row">
              <div class="col-sm-12">
                <h2>{{ age_at_inclusion.title }}</h2>
                <BarChart
                  chartId="age-at-inclusion"
                  :chartData="age_at_inclusion.data"
                  xvar="label"
                  yvar="value"
                  xAxisLabel="Age Groups"
                  yAxisLabel="Number of Patients"
                />
              </div>
            </div>
          </div>
        </div>
        <div class="row">
          <DataTable
            tableId="patients-registry"
            :data="patients_registry.data"
            :columnOrder='["Thematic Disease Groups", "Number of Patients"]'
            :caption="patients_registry.title"
          />
        </div>
      </main>
    </div>
</template>

<script>
import DataTable from './components/Datatable.vue'
import PieChart from './components/VizPieChart.vue'
import BarChart from './components/VizBarChart.vue'

export default {
  data () {
    return {
      country_enrollment: {},
      hcp_enrollment: {},
      patients_registry: {},
      sex_at_birth: {},
      age_at_inclusion: {}
    }
  },
  components: {
    DataTable,
    PieChart,
    BarChart
  },
  methods: {
    async fetchData (url) {
      const response = await fetch(url)
      const data = response.json()
      return data
    },
    extractData (data) {
      return {
        title: data.items[0].title,
        data: data.items
      }
    },
    setLabels (data, labelMappings) {
      data.forEach(row => {
        labelMappings.forEach((labelMap) => {
          row[labelMap.newKey] = row[labelMap.oldKey]
          delete data[labelMap.oldKey]
        })
      })
      return data
    }
  },
  mounted () {
    Promise.all([
      this.fetchData('/api/v2/ernstats_statistics?q=dashboardElement==table_country_enrollment'),
      this.fetchData('/api/v2/ernstats_statistics?q=dashboardElement==table_hcp_enrollment'),
      this.fetchData('/api/v2/ernstats_statistics?q=dashboardElement==number_patients_genturis_registry'),
      this.fetchData('/api/v2/ernstats_statistics?q=dashboardElement==pie_sex_at_birth'),
      this.fetchData('/api/v2/ernstats_statistics?q=dashboardElement==barchart_age_at_inclusion')
    ]).then(result => {
      this.country_enrollment = this.extractData(result[0])
      this.hcp_enrollment = this.extractData(result[1])

      // prepare data for disease group counts
      const extractedPatientData = this.extractData(result[2])
      extractedPatientData.data = this.setLabels(
        extractedPatientData.data,
        [
          { oldKey: 'label', newKey: 'Thematic Disease Groups' },
          { oldKey: 'value', newKey: 'Number of Patients' }
        ]
      )
      this.patients_registry = extractedPatientData
      
      // process set at birth data
      this.sex_at_birth = this.extractData(result[3])
      const sexAtBirthPieChartData = {}
      this.sex_at_birth.data.forEach(row => {
        sexAtBirthPieChartData[row.label] = row.value
      })
      this.sex_at_birth.data = sexAtBirthPieChartData
      
      // process age at time of inclusion data
      this.age_at_inclusion = this.extractData(result[4])
    })
  }
}
</script>

<style lang="scss">
.row, .col-sm-6 {
  border: 1px solid #bdbdbd;
}

</style>
