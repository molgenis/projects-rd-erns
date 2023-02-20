# Model Schema

## Packages

| Name | Description | Parent |
|:---- |:-----------|:------|
| ernstats | Descriptives on enrolled patients and data providers (v1.3.0, 2023-02-20) | - |

## Entities

| Name | Description | Package |
|:---- |:-----------|:-------|
| dataproviders | All affiliated data providers (intitutions, hospitals, etc.) | ernstats |
| inclusionCriteria | Define or modify inclusion criteria for each subgroup | ernstats |
| stats | Stats used in the dashboard | ernstats |

## Attributes

### Entity: ernstats_dataproviders

All affiliated data providers (intitutions, hospitals, etc.)

| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| id&#8251; | - | identifier of the institution from ROR | - |
| databaseID | - | The identifier of the emx package for this organisation | - |
| projectName | - | Original institution name as defined by the project | string |
| hasSubmittedData | - | An indication that a file has been submitted to a data repository. | bool |
| organisationInfo | - | - | compound |
| centerType | - | - | string |
| centerRepresentative | - | - | string |
| iri | - | A unique symbol that establishes identity of the resource. | hyperlink |
| codesystem | - | A systematized collection of concepts that define corresponding codes. | - |
| code | - | identifier of the institution from ROR | - |
| additionalInformation | - | - | compound |
| displayName | - | The standardized text associated with a code in a particular code system. | string |
| officialName | - | An established society, corporation, foundation or other organization founded and united for a specific purpose, e.g. for health-related research; also used to refer to a building or buildings occupied or used by such organization. | string |
| centerProjectUrl | - | - | hyperlink |
| centerLocation | - | - | compound |
| city | - | A large and densely populated urban area; a city specified in an address. | string |
| country | - | A collective generic term that refers here to a wide variety of dependencies, areas of special sovereignty, uninhabited islands, and other entities in addition to the traditional countries or independent states. | string |
| latitude | - | The angular distance north or south between an imaginary line around a heavenly body parallel to its equator and the equator itself. | decimal |
| longitude | - | An imaginary great circle on the surface of a heavenly body passing through the poles at right angles to the equator. | decimal |

### Entity: ernstats_inclusionCriteria

Define or modify inclusion criteria for each subgroup

| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| _id&#8251; | - | table row identifier | - |
| groupID | - | A unique ID used to identify a group | - |
| groupName | - | Name of the group | - |
| criteria | - | - | compound |
| type | - | A variable to identify criteria for a specific group (e.g., "genes", "disease", etc.) | - |
| value | - | values used to select rows (IDs, codes, etc.) | - |
| label | - | additional context that describes the criteria | - |

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

