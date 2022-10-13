<template>
  <Page id="dashboard-container">
    <LoadingScreen v-if="loading"/>
    <div class="error-message" v-else-if="!loading & loadingError">
      <p><strong>Unable to retrive data</strong></p>
      <output>{{ loadingError }}</output>
    </div>
    <Dashboard id="ern-dashboard" :loading="loading" v-else>
      <DataHighlightContainer id="ern-data-highlights" aria-labelledby="ern-highlights-title">
        <p id="ern-highlights-title" class="visually-hidden">
          summary of enrollment for the ERN Genturis registry. This includes total patients to date, total number of actively enrolling countries, and the total number of healthcare providers enrolling patient.
        </p>
        <DataHighlightBox
          id="enrolled-patients"
          title="Total Patients Enrolled"
          :value="`${patientEnrollment}`"
        />
        <DataHighlightBox
          id="enrollment-by-countries"
          title="Countries Enrolling"
          :value="`${countryEnrollment}`"
        />
        <DataHighlightBox
          id="enrollment-by-patients"
          title="Healthcare Providers Enrolling"
          :value="`${providersEnrollment}`"
        />
      </DataHighlightContainer>
      <DashboardSection
        id="viz-map"
        aria-labelledBy="viz-map-title"
      >
        <h2 id="viz-map-title" class="chart-title">
          Status of Data Submitted by Healthcare Providers
        </h2>
          <GeoMercator
            chartId="ern-institutions"
            :chartData="institutionGeoData"
            :geojson="geojson"
            fillVariable="fillColor"
            :chartWidth="475"
            :chartHeight="535"
            :chartSize="114"
            :chartCenterCoordinates="[6, 53]"
            :legendLabels="['Data Submitted', 'No Data']"
            :legendColors="['#E9724C', '#f0f0f0']"
          />
      </DashboardSection>
      <DashboardSection id="viz-pie-chart">
        <h2 id="sex-at-birth-title" class="chart-title centered">Sex at Birth</h2>
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
        <h2 id="age-at-inclusion-title" class="chart-title centered">
          Age of Patients at Time of Inclusion
        </h2>
        <BarChart
          chartId="age-at-inclusion-chart"
          :chartData="ageAtInclusion.data"
          :chartHeight="250"
          :chartWidth="600"
          :chartMargins="{top: 10, right: 10, bottom: 60, left: 60}"
          barFill="#335598"
          barHoverFill="#45A5C8"
          xvar="label"
          yvar="value"
          :yMax="50"
          xAxisLabel="Age Groups"
          yAxisLabel="Number of Patients"
        />
      </DashboardSection>
      <DashboardSection id="viz-table-disease-enrollment">
        <h2 id="patient-enrollment-summary-title" class="chart-title">
          Summary of Patients Enrolled by Thematic Disease Group
        </h2>
        <DataTable
          tableId="disease-group-enrollment-table"
          class="ern-table-dataset"
          :data="diseaseGroupEnrollment.data"
          :columnOrder='["Thematic Disease Groups", "Number of Patients"]'
        />
      </DashboardSection>
    </Dashboard>
  </Page>
</template>

<script>
import Page from '../components/Page.vue'
import LoadingScreen from '../components/LoadingScreen.vue'
import Dashboard from '../components/Dashboard.vue'
import DashboardSection from '../components/DashboardSection.vue'
import DataHighlightBox from '../components/DataHighlightBox.vue'
import DataHighlightContainer from '../components/DataHighlightContainer.vue'
import DataTable from '../components/Datatable.vue'
import PieChart from '../components/VizPieChart.vue'
import BarChart from '../components/VizBarChart.vue'
import GeoMercator from '../components/VizGeoMercator.vue'
import geojson from '../assets/europe.custom.geojson'

export default {
  name: 'ern-dashboard',
  components: {
    Page,
    LoadingScreen,
    Dashboard,
    DashboardSection,
    DataHighlightBox,
    DataHighlightContainer,
    DataTable,
    PieChart,
    BarChart,
    GeoMercator
  },
  data () {
    return {
      loading: true,
      loadingError: null,
      institutionGeoData: [],
      patientEnrollment: null,
      countryEnrollment: null,
      providersEnrollment: null,
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
    },
    sortData (data, column) {
      return data.sort((current, next) => {
        return current[column] < next[column] ? -1 : 1
      })
    }
  },
  mounted () {
    Promise.all([
      this.fetchData('/api/v2/ernstats_stats'),
      this.fetchData('/api/v2/ernstats_dataproviders')
    ]).then(response => {
      const data = response[0].items
      const mapData = response[1].items
      
      this.institutionGeoData = mapData.map(row => ({
        ...row, fillColor: row.hasSubmittedData ? '#E9724C' : '#f0f0f0'
      }))
      console.log(this.institutionGeoData)

      const patientEnrollment = this.subsetData(data, 'table-enrollment-patients')
      const countryEnrollment = this.subsetData(data, 'table-enrollment-country')
      const providersEnrollment = this.subsetData(data, 'table-enrollment-providers')
      const diseaseGroupEnrollmentData = this.subsetData(data, 'table-enrollment-disease-group')
      const sexAtBirthData = this.subsetData(data, 'pie-sex-at-birth')
      const ageAtInclusionData = this.subsetData(data, 'barchart-age')
      
      this.patientEnrollment = patientEnrollment[0].value
      this.countryEnrollment = countryEnrollment[0].value
      this.providersEnrollment = providersEnrollment[0].value

      this.diseaseGroupEnrollment = this.extractData(diseaseGroupEnrollmentData)
      this.diseaseGroupEnrollment.data = this.sortData(this.diseaseGroupEnrollment.data, 'valueOrder')
      this.renameKey(this.diseaseGroupEnrollment.data, 'label', 'Thematic Disease Groups')
      this.renameKey(this.diseaseGroupEnrollment.data, 'value', 'Number of Patients')

      this.sexAtBirth.title = sexAtBirthData[0].title
      this.sexAtBirth.data = this.asDataObject(sexAtBirthData, 'label', 'value')

      this.ageAtInclusion = this.extractData(ageAtInclusionData)
      this.ageAtInclusion.data = this.sortData(this.ageAtInclusion.data, 'valueOrder')
    }).then(() => {
      this.loading = false
    }).catch(error => {
      this.loading = false
      this.loadingError = error
    })
  }
}
</script>

<style lang="scss">

.chart-title {
  font-size: 14pt;
  font-weight: bold;
  line-height: 1.4;
  letter-spacing: 0.03em;
  color: $gray-900;
  margin: 12px 0;
  
  &.centered {
    text-align: center;
  }
}

.ern-table-summary {
  table {
    caption {
      box-sizing: border-box;
      padding: 6px 12px;
      color: #355cb8;
      background-color: hsl(222, 55%, 94%);
      font-size: 11pt;
      border-radius: 2px;
      margin: 0;
    }
    tbody {
      background-color: #f6f6f6;
    }
  }
}

.ern-table-dataset {
  table {
    tbody {
      tr:last-child {
        td {
          border-top: 1px solid #252525;
          font-weight: bold;
        }
      }
    }
  }
}

#ern-dashboard {
  background-color: #f6f6f6;
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-areas:
    "highlights highlights"
    "map piechart"
    "map barchart"
    "table table";

  $gap: 1.6em;
  column-gap: $gap;
  row-gap: $gap;
  
  @media screen and (max-width: 824px) {
    grid-template-columns: 1fr;
    grid-template-areas:
      "highlights"
      "map"
      "piechart"
      "barchart"
      "table";
  }
}

#ern-data-highlights {
  grid-area: highlights;
}

#viz-map {
  grid-area: map;
}

#viz-pie-chart {
  grid-area: piechart;
}

#viz-age-bar-chart {
  grid-area: barchart;
}

#viz-table-disease-enrollment {
  grid-area: table;
}

#disease-group-enrollment-table {
  thead {
    tr {
      th[data-column-index="1"] {
        text-align: right;
      }
    }
  }
}
</style>
