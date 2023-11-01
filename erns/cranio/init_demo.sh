#!/bin/sh

HOST="...."
USER_NAME="...."
USER_PASS='....'

# ~ 1 ~
# sign in and retrieve token for sending additional requests
# NOTE: Set username and password
TOKEN=$(curl -s "${HOST}/api/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation{ signin(email:\"'${USER_NAME}'\", password:\"'${USER_PASS}'\"){ message token } }"}' | python -c "import sys,json; data=json.load(sys.stdin); print(data['data']['signin']['token'])"
)

# ~ 2 ~
# Create new schema from ERN_DASHBOARD: the schema name is hard coded into the vue apps
curl "${HOST}/api/graphql" \
  -H "x-molgenis-token:${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation{createSchema(name:\"CranioStats\",template:\"ERN_DASHBOARD\",includeDemoData:false){message}}"}'
  
# ~ 3 ~
# Creating a new schemas using the 7 starting institutions + Erasmus
declare -a SCHEMA_IDS=("BE1" "CZ1" "DE1" "HU2" "IT2" "IT5" "NL1" "NL3")
declare -a SCHEMA_NAMES=(
  "UZ Leuven"
  "University Hospital Motol"
  "Universitatsklinikum Charite"
  "Szent-Gyorgyi Albert Medical Center"
  "Fondazione A. Gemelli"
  "Ospedale San Gerardo Monza"
  "Erasmus MC"
  "UMC Utrecht"
)

# create empty schema (replace with template later) and make the schema viewable as anonymous
INDEX=1
for SCHEMA in "${SCHEMA_IDS[@]}"
do
  NAME="${SCHEMA_NAMES[$INDEX]}"
  curl -s "${HOST}/api/graphql" \
    -H "Content-Type: application/json" \
    -H "x-molgenis-token:${TOKEN}" \
    -d '{"query":"mutation{createSchema(name:\"'${SCHEMA}'\",description:\"'${NAME}'\"){ message }}"}'

  curl -s "${HOST}/${SCHEMA}/api/graphql" \
    -H "Content-Type: application/json" \
    -H "x-molgenis-token:${TOKEN}" \
    -d '{"query": "mutation{change(members:[{email:\"anonymous\",role:\"Viewer\"}]){message}}"}'
    
  ((INDEX++))
done
