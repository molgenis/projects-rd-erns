<template>
  <div id="dashboard-container">
    <div class="loading-screen" v-if="loading">
      <div class="loading-screen-content">
        <div class="loading-screen-spinner">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="spinner-gear"
            fill="none"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
            />
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
            />
          </svg>
        </div>
        <p class="message">Loading</p>
      </div>
    </div>
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
            :geojson="geojson"
            :chartWidth="400"
            :chartHeight="400"
            :chartSize="114"
            :chartCenterCoordinates="[6, 53]"
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
          :chartHeight="200"
          :chartWidth="300"
          :chartMargins="5"
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
          :chartHeight="250"
          :chartWidth="600"
          :chartMargins="{top: 10, right: 10, bottom: 60, left: 60}"
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
import DataTable from './components/Datatable.vue'
import PieChart from './components/VizPieChart.vue'
import BarChart from './components/VizBarChart.vue'
import GeoMercator from './components/VizGeoMercator.vue'
import ChartLegend from './components/VizLegend.vue'

import geojson from './assets/europe.custom.geojson'

import './styles/styles.scss'

export default {
  name: 'ern-dashboard',
  components: {
    DashboardUI,
    DashboardSection,
    DataTable,
    PieChart,
    BarChart,
    GeoMercator,
    ChartLegend
  },
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
      },
      geojson: geojson
    }
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
      return data.filter(row => row.component === value)
    }
  },
  mounted () {
    Promise.all([
      this.fetchData('/api/v2/ernstats_stats'),
      this.fetchData('/api/v2/ernstats_dataproviders')
    ]).then(response => {
      const data = response[0].items
      const mapData = response[1].items
      this.institutionGeoData = mapData

      const countryEnrollmentData = this.subsetData(data, 'table-enrollment-country')
      const healthcareProvidersData = this.subsetData(data, 'table-enrollment-providers')
      const diseaseGroupEnrollmentData = this.subsetData(data, 'table-enrollment-disease-group')
      const sexAtBirthData = this.subsetData(data, 'pie-sex-at-birth')
      const ageAtInclusionData = this.subsetData(data, 'barchart-age')
      
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

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.loading-screen {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100vh;
  background-color: hsl(220, 50%, 88%);
  color: hsl(220, 50%, 18%);
  opacity: 0.8;
  
  .loading-screen-content {
    width: 90%;
    margin: 0 auto;
    z-index: 1;
    text-align: center;
    
    $icon-size: 62px;
    .spinner-gear {
      width: $icon-size;
      height: $icon-size;
      transform-origin: center;
      animation: spin 6s linear infinite;
    }
    
    .message {
      font-size: 18pt;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-weight: bold;
    }
  }
}
</style>
