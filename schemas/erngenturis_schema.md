# Model Schema

## Packages

| Name | Description | Parent |
|:---- |:-----------|:------|
| ernstats | Descriptives on enrolled patients and data providers (v1.1.1, 2022-10-10) | - |

## Entities

| Name | Description | Package |
|:---- |:-----------|:-------|
| dataproviders | All affiliated data providers (intitutions, hospitals, etc.) | ernstats |
| stats | Stats used in the dashboard | ernstats |

## Attributes

### Entity: ernstats_dataproviders

All affiliated data providers (intitutions, hospitals, etc.)

| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| name&#8251; | - | An established society, corporation, foundation or other organization founded and united for a specific purpose, e.g. for health-related research; also used to refer to a building or buildings occupied or used by such organization. | string |
| displayName | - | The standardized text associated with a code in a particular code system. | string |
| hasSubmittedData | - | An indication that a file has been submitted to a data repository. | bool |
| city | - | A large and densely populated urban area; a city specified in an address. | string |
| country | - | A collective generic term that refers here to a wide variety of dependencies, areas of special sovereignty, uninhabited islands, and other entities in addition to the traditional countries or independent states. | string |
| longitude | - | An imaginary great circle on the surface of a heavenly body passing through the poles at right angles to the equator. | decimal |
| latitude | - | The angular distance north or south between an imaginary line around a heavenly body parallel to its equator and the equator itself. | decimal |
| codesystem | - | A systematized collection of concepts that define corresponding codes. | - |
| code | - | A symbol or combination of symbols which is assigned to the members of a collection. | - |
| iri | - | A unique symbol that establishes identity of the resource. | hyperlink |
| projectName | - | Original institution name as defined by the GENTURIS project (prior to cleaning) | string |

### Entity: ernstats_stats

Stats used in the dashboard

| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| id&#8251; | - | - | - |
| title | - | title to be rendered into the app (e.g., section heading, component title, table heading, etc) | string |
| label | - | string that describes the value | string |
| value | - | raw data value | decimal |
| valueOrder | - | integer specifying the order of a value in an array (ideal for tables, charts) | int |
| component | - | name of the component that the current will be used in | string |
| description | - | additional information about this record | text |

Note: The symbol &#8251; denotes attributes that are primary keys

