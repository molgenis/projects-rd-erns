<template>
    <div id="dashboard-container">
      <LoadingScreen v-if="loading" />
      <DashboardUI id="ern-dashboard" :loading="loading" v-else>
        <DashboardSection
          id="viz-map"
          aria-labelledBy="viz-map-title"
        >
          <h2 id="viz-map-title" class="chart-title">
            Status of data submitted by Healthcare Providers
          </h2>
            <GeoMercator
              chartId="ern-institutions"
              :chartData="institutionGeoData"
              :chartWidth="400"
              :chartHeight="700"
              :chartCenterCoordinates="[6, 54]"
            />
            <ChartLegend
              :labels="['Data Submitted', 'No Data']"
              :colors="['#3b3b3b', '#94a6da']"
            />
        </DashboardSection>
        <DashboardSection id="viz-table-patient-enrollment">
          <h2 id="patient-enrollment-summary-title" class="visually-hidden">
            Summaries on Patient Enrollment
          </h2>
          <DataTable
            tableId="country-enrollment"
            class="ern-table-summary"
            :data="countryEnrollment.data"
            :columnOrder='["label","value"]'
            :caption="countryEnrollment.title"
            :visuallyHideHeader="true"
          />
        </DashboardSection>
        <DashboardSection id="viz-table-hcp-enrollment">
          <DataTable
            tableId="hcp-enrollment"
            class="ern-table-summary"
            :data="healthcareProvidersEnrollment.data"
            :columnOrder='["label", "value"]'
            :caption="healthcareProvidersEnrollment.title"
            :visuallyHideHeader="true"
          />
        </DashboardSection>
        <DashboardSection id="viz-pie-chart">
          <h2 id="sex-at-birth-title" class="chart-title">
            {{ sexAtBirth.title }}
          </h2>
          <PieChart
            chartId="sex-at-birth-chart"
            :chartData="sexAtBirth.data"
            class="m-auto"
            :chartColors="['#d7e0f1', '#355cb8', '#7e98d4']"
          />
        </DashboardSection>
        <DashboardSection id="viz-age-bar-chart">
          <h2 id="age-at-inclusion-title" class="chart-title">
            {{ ageAtInclusion.title }}
          </h2>
          <BarChart
            chartId="age-at-inclusion-chart"
            :chartData="ageAtInclusion.data"
            :chartHeight="350"
            :chartWidth="600"
            barFill="#355cb8"
            xvar="label"
            yvar="value"
            xAxisLabel="Age Groups"
            yAxisLabel="Number of Patients"
          />
        </DashboardSection>
        <DashboardSection id="viz-table-disease-enrollment">
          <h2 id="patient-enrollment-summary-title" class="visually-hidden">
            Summary of patients enrolled by thematic disease group
          </h2>
          <DataTable
            tableId="disease-group-enrollment-table"
            class="ern-table-dataset"
            :data="diseaseGroupEnrollment.data"
            :columnOrder='["Thematic Disease Groups", "Number of Patients"]'
            :caption="diseaseGroupEnrollment.title"
          />
        </DashboardSection>
      </DashboardUI>
    </div>
</template>

<script>
import DashboardUI from './components/Dashboard.vue'
import DashboardSection from './components/DashboardSection.vue'
import LoadingScreen from './components/LoadingScreen.vue'
import DataTable from './components/Datatable.vue'
import PieChart from './components/VizPieChart.vue'
import BarChart from './components/VizBarChart.vue'
import GeoMercator from './components/VizGeoMercator.vue'
import ChartLegend from './components/VizLegend.vue'

import './styles/styles.scss'

export default {
  data () {
    return {
      loading: true,
      institutionGeoData: [],
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
    DashboardUI,
    DashboardSection,
    LoadingScreen,
    DataTable,
    PieChart,
    BarChart,
    GeoMercator,
    ChartLegend
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
    extractData (data) {
      const datasetName = data[0].title
      return {
        title: datasetName,
        data: data
      }
    },
    renameKey (data, oldKey, newKey) {
      data.forEach(row => delete Object.assign(row, { [newKey]: row[oldKey] })[oldKey])
    },
    subsetData (data, value) {
      return data.filter(row => row.dashboardElement === value)
    }
  },
  mounted () {
    Promise.all([
      this.fetchData('/api/v2/ernstats_statistics'),
      this.fetchData('/api/v2/ernstats_hcps')
    ]).then(response => {
      const data = response[0].items
      const mapData = response[1].items
      this.institutionGeoData = mapData

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
