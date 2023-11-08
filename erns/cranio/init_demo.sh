#!/bin/sh

HOST=""
USER_NAME=""
USER_PASS=""

# ~ 1 ~
# sign in and retrieve token for sending additional requests
# NOTE: Set username and password
TOKEN=$(curl -s "${HOST}/api/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation{ signin(email:\"'${USER_NAME}'\", password:\"'${USER_PASS}'\"){ message token } }"}' \
  | grep "token" | tr -d '"' | awk '{print $3}'
)

# //////////////////////////////////////

# ~ 2 ~
# Delete existing schemas
declare -a SCHEMAS_TO_REMOVE=(
  "catalogue-demo"
  "CatalogueOntologies"
  "pet store"
)

for SCHEMA in "${SCHEMAS_TO_REMOVE[@]}"
do
  curl -s "${HOST}/api/graphql" \
    -H "x-molgenis-token:${TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{"query":"mutation{deleteSchema(name:\"'${SCHEMA}'\"){message}}"}'
done

# //////////////////////////////////////

# ~ 3 ~
# Create new schema from ERN_DASHBOARD: the schema name is hard coded into the vue apps
curl "${HOST}/api/graphql" \
  -H "x-molgenis-token:${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation{createSchema(name:\"CranioStats\",template:\"ERN_DASHBOARD\"){message}}"}'
  
curl -s "${HOST}/api/graphql" \
  -H "Content-Type: application/json" \
  -H "x-molgenis-token:${TOKEN}" \
  -d '{"query":"mutation{updateSchema(name:\"CranioStats\",description:\"Staging Tables for Dashboards\"){ message }}"}'


# import data
curl "${HOST}/${SCHEMA}/api/graphql" \
  -H "Content-Type: multipart/form-data" \
  -H "x-molgenis-token:${TOKEN}" \
  -F "content=@erns/cranio/cranio_emx2.xlsx"

# prepare payload for customising the menu
PUBLIC_MENU='[{\\\"label\\\":\\\"Home\\\",\\\"href\\\":\\\"./cranio-public\\\",\\\"role\\\":\\\"Viewer\\\"},{\\\"label\\\":\\\"Tables\\\",\\\"href\\\":\\\"tables\\\",\\\"role\\\":\\\"Viewer\\\"},{\\\"label\\\":\\\"Schema\\\",\\\"href\\\":\\\"schema\\\",\\\"role\\\":\\\"Manager\\\"},{\\\"label\\\":\\\"Up/Download\\\",\\\"href\\\":\\\"updownload\\\",\\\"role\\\":\\\"Editor\\\"},{\\\"label\\\":\\\"Graphql\\\",\\\"href\\\":\\\"graphql-playground\\\",\\\"role\\\":\\\"Viewer\\\"},{\\\"label\\\":\\\"Settings\\\",\\\"href\\\":\\\"settings\\\",\\\"role\\\":\\\"Manager\\\"},{\\\"label\\\":\\\"Help\\\",\\\"href\\\":\\\"docs\\\",\\\"role\\\":\\\"Viewer\\\"}]'

# update the navlinks
curl -s "${HOST}/CranioStats/api/graphql" \
  -H "Content-Type: application/json" \
  -H "x-molgenis-token:${TOKEN}" \
  -d '{"query": "mutation{change(settings:[{key:\"menu\",value:\"'${PUBLIC_MENU}'\"}]){message}}"}'

# //////////////////////////////////////
  
# ~ 4 ~
# Creating a new schemas using the 7 starting institutions + Erasmus
# create empty schema (replace with template later) and make the schema viewable as anonymous

# set provider-level menu
PROVIDER_MENU='[{\\\"label\\\":\\\"Home\\\",\\\"href\\\":\\\"./cranio-provider\\\",\\\"role\\\":\\\"Viewer\\\"},{\\\"label\\\":\\\"Tables\\\",\\\"href\\\":\\\"tables\\\",\\\"role\\\":\\\"Viewer\\\"},{\\\"label\\\":\\\"Schema\\\",\\\"href\\\":\\\"schema\\\",\\\"role\\\":\\\"Manager\\\"},{\\\"label\\\":\\\"Up/Download\\\",\\\"href\\\":\\\"updownload\\\",\\\"role\\\":\\\"Editor\\\"},{\\\"label\\\":\\\"Graphql\\\",\\\"href\\\":\\\"graphql-playground\\\",\\\"role\\\":\\\"Viewer\\\"},{\\\"label\\\":\\\"Settings\\\",\\\"href\\\":\\\"settings\\\",\\\"role\\\":\\\"Manager\\\"},{\\\"label\\\":\\\"Help\\\",\\\"href\\\":\\\"docs\\\",\\\"role\\\":\\\"Viewer\\\"}]'

declare -a SCHEMA_IDS=(
  "BE3"
  "CZ1"
  "DE1"
  "HU1"
  "IT4"
  "IT6"
  "NL2"
  "NL4"
)
declare -a SCHEMA_NAMES=(
  "UZ Leuven"
  "University Hospital Motol "
  "Charité Universitätsmedizin Berlin"
  "Szent-Györgyi Albert Medical Center, University of Szeged"
  "Fondazione Policlinico Universitario A. Gemelli "
  "San Gerardo Hospital"
  "Erasmus MC"
  "UMC Utrecht"
)

INDEX=1
for SCHEMA in "${SCHEMA_IDS[@]}"
do
  NAME="${SCHEMA_NAMES[$INDEX]}"
  echo "Creating schema for ${NAME} (${SCHEMA})"
  
  curl -s "${HOST}/api/graphql" \
    -H "Content-Type: application/json" \
    -H "x-molgenis-token:${TOKEN}" \
    -d '{"query":"mutation{createSchema(name:\"'${SCHEMA}'\"){ message }}"}'
    
  wait

  curl -s "${HOST}/api/graphql" \
    -H "Content-Type: application/json" \
    -H "x-molgenis-token:${TOKEN}" \
    -d '{"query":"mutation{updateSchema(name:\"'${SCHEMA}'\",description:\"'${NAME}'\"){ message }}"}'

  curl -s "${HOST}/${SCHEMA}/api/graphql" \
    -H "Content-Type: application/json" \
    -H "x-molgenis-token:${TOKEN}" \
    -d '{"query": "mutation{change(members:[{email:\"anonymous\",role:\"Viewer\"}]){message}}"}'

  curl -s "${HOST}/${SCHEMA}/api/graphql" \
    -H "Content-Type: application/json" \
    -H "x-molgenis-token:${TOKEN}" \
    -d '{"query": "mutation{change(settings:[{key:\"menu\",value:\"'${PROVIDER_MENU}'\"}]){message}}"}'

  ((INDEX++))
done

