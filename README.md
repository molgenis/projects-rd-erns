# projects-rd-erns

This repository contains data models, code, and scripts for managing MOLGENIS
instances ERNs. ERN-specific files are located in the `erns` folder and EMX1
and EMX2 resources are included.

## ERN Dashboard Data Model

There are two versions of the ERN dashboard model (EMX1 and EMX2). The EMX2
source is located here, but it is copied in to the molgenis-emx2 repository.

## Notes

For the map component in the dashboards, you will need to have the latest
geospatial file of European Territories. See
[https://github.com/AshKyd/geojson-regions](https://github.com/AshKyd/geojson-regions)
for more information. The geojson file was further modified using
[mapshaper.org](https://mapshaper.org/) to remove countries that weren't
necessary to display in the view.
