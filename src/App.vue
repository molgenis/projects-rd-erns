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
                    :data="healthcareProvidersEnrollment.data"
                    :columnOrder='["label", "value"]'
                    :caption="healthcareProvidersEnrollment.title"
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
            :data="diseaseGroupEnrollment.data"
            :columnOrder='["Thematic Disease Groups", "Number of Patients"]'
            :caption="diseaseGroupEnrollment.title"
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
      loading: true,
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
    asDataObject (data, key, value) {
      const newDataObject = {}
      data.forEach(row => { newDataObject[row[key]] = row[value] })
      return newDataObject
    },
    subsetData (data, value) {
      return data.filter(row => row.dashboardElement === value)
    },
    extractData (data) {
      const datasetTitle = data[0].title
      return {
        title: datasetTitle,
        data: data
      }
    },
    renameKey (data, oldKey, newKey) {
      data.forEach(row => delete Object.assign(row, { [newKey]: row[oldKey] })[oldKey])
    }
  },
  mounted () {
    Promise.all([
      this.fetchData('/api/v2/ernstats_statistics')
    ]).then(result => {
      const data = result[0].items

      const countryEnrollmentData = this.subsetData(data, 'table_country_enrollment')
      const healthcareProvidersData = this.subsetData(data, 'table_hcp_enrollment')
      const diseaseGroupEnrollmentData = this.subsetData(data, 'number_patients_genturis_registry')
      const sexAtBirthData = this.subsetData(data, 'pie_sex_at_birth')
      const ageAtInclusionData = this.subsetData(data, 'barchart_age_at_inclusion')
      
      this.countryEnrollment = this.extractData(countryEnrollmentData)
      this.healthcareProvidersEnrollment = this.extractData(healthcareProvidersData)

      this.diseaseGroupEnrollment = this.extractData(diseaseGroupEnrollmentData)
      this.renameKey(this.diseaseGroupEnrollment.data, 'label', 'Thematic Disease Groups')
      this.renameKey(this.diseaseGroupEnrollment.data, 'value', 'Number of Patients')

      this.sexAtBirth.title = sexAtBirthData[0].title
      this.sexAtBirth.data = this.asDataObject(sexAtBirthData, 'label', 'value')

      this.ageAtInclusion = this.extractData(ageAtInclusionData)
    }).then(() => {
      this.loading = false
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
