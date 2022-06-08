<template>
    <div id="dashboard">
      <LoadingScreen v-if="loading" />
      <main class="container-fluid" v-else>
        <div class="row">
          <section class="col-sm-5">
            <h2 class="visually-hidden">Map of Institutions</h2>
            <p>[insert map here]</p>
          </section>
          <div class="col-sm-7">
            <div class="row">
              <section id="patient-enrollment-summary" class="col-sm-5" aria-labelledBy="patient-enrollment-summary-title">
                <h2 id="patient-enrollment-summary-title" class="visually-hidden">
                  Summaries on Patient Enrollment
                </h2>
                <div class="row">
                  <DataTable
                    tableId="country-enrollment"
                    :data="countryEnrollment.data"
                    :columnOrder='["label","value"]'
                    :caption="countryEnrollment.title"
                    :visuallyHideHeader="true"
                  />
                </div>
                <div class="row">
                  <DataTable
                    tableId="hcp-enrollment"
                    :data="hcpEnrollment.data"
                    :columnOrder='["label", "value"]'
                    :caption="hcpEnrollment.title"
                    :visuallyHideHeader="true"
                  />
                </div>
              </section>
              <section id="sex-at-birth" aria-labelledBy="sex-at-birth-title" class="col-sm-7">
                <h2 id="sex-at-birth-title" class="chart-title">
                  {{ sexAtBirth.title }}
                </h2>
                <PieChart
                  chartId="sex-at-birth-chart"
                  :chartData="sexAtBirth.data"
                />
              </section>
            </div>
            <div class="row">
              <section id="age-at-inclusion" aria-labelledBy="age-at-inclusion-title" class="col-sm-12">
                <h2 id="age-at-inclusion-title" class="chart-title">
                  {{ ageAtInclusion.title }}
                </h2>
                <BarChart
                  chartId="age-at-inclusion-chart"
                  :chartData="ageAtInclusion.data"
                  xvar="label"
                  yvar="value"
                  xAxisLabel="Age Groups"
                  yAxisLabel="Number of Patients"
                />
              </section>
            </div>
          </div>
        </div>
        <section id="patient-enrollment-summary" aria-labelledBy="patient-enrollment-summary-title" class="row">
          <h2 id="patient-enrollment-summary-title" class="visually-hidden">
            Summary of patients enrolled by thematic disease group
          </h2>
          <DataTable
            tableId="patients-registry"
            :data="patientsRegistry.data"
            :columnOrder='["Thematic Disease Groups", "Number of Patients"]'
            :caption="patientsRegistry.title"
          />
        </section>
      </main>
    </div>
</template>

<script>
import LoadingScreen from './components/LoadingScreen.vue'
import DataTable from './components/Datatable.vue'
import PieChart from './components/VizPieChart.vue'
import BarChart from './components/VizBarChart.vue'

export default {
  data () {
    return {
      // loading: true,
      loading: false,
      countryEnrollment: {
        title: null,
        data: []
      },
      hcpEnrollment: {
        title: null,
        data: []
      },
      sexAtBirth: {
        title: null,
        data: {}
      },
      ageAtInclusion: {
        title: null,
        data: []
      },
      patientsRegistry: {
        title: null,
        data: []
      }
    }
  },
  components: {
    LoadingScreen,
    DataTable,
    PieChart,
    BarChart
  },
  methods: {
    async fetchData (url) {
      const response = await fetch(url)
      return response.json()
    },
    extractData (data) {
      return {
        title: data.items[0].title,
        data: data.items
      }
    },
    renameKeys (data, labelMappings) {
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
      this.countryEnrollment = this.extractData(result[0])
      this.hcpEnrollment = this.extractData(result[1])

      // prepare data for disease group counts
      const newLabels = [
        { oldKey: 'label', newKey: 'Thematic Disease Groups' },
        { oldKey: 'value', newKey: 'Number of Patients' }
      ]
      const extractedPatientData = this.extractData(result[2])
      extractedPatientData.data = this.renameKeys(
        extractedPatientData.data, newLabels
      )
      this.patientsRegistry = extractedPatientData
      
      // process set at birth data
      this.sexAtBirth.title = result[3].items[0].title
      const pieChartData = {}
      result[3].items.forEach(row => {
        pieChartData[row.label] = row.value
      })
      this.sexAtBirth.data = pieChartData
      
      // process age at time of inclusion data
      this.ageAtInclusion = this.extractData(result[4])
    }).then(() => {
      setTimeout(() => {
        this.loading = false
      }, 450)
    })
  }
}
</script>

<style lang="scss">

.visually-hidden {
  position: absolute;
  clip: rect(1px 1px 1px 1px); /* IE6, IE7 */
  clip: rect(1px, 1px, 1px, 1px);
  overflow: hidden;
  height: 1px;
  width: 1px;
  margin: -1px;
  white-space: nowrap;
}

.row, .col-sm-6 {
  border: 1px solid #bdbdbd;
}

.chart-title {
  font-size: 14pt;
  font-weight: bold;
  line-height: 1.4;
  letter-spacing: 0.03em;
  text-align: center;
  padding: 1em 0;
}

#dashboard {
  background-color: #f6f6f6;
}

</style>
