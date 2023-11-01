#!/bin/sh

HOST="...."
USER_NAME="...."
USER_PASS="..."

# ~ 1 ~
# sign in and retrieve token for sending additional requests
# NOTE: Set username and password
TOKEN=$(curl -s "${HOST}/api/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation{ signin(email:\"'${USER_NAME}'\", password:\"'${USER_PASS}'\"){ message token } }"}' \
  | grep "token" | tr -d '"' | awk '{print $3}'
)

# ~ 2 ~
# Create new schema from ERN_DASHBOARD: the schema name is hard coded into the vue apps
curl "${HOST}/api/graphql" \
  -H "x-molgenis-token:${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation{createSchema(name:\"CranioStats\",template:\"ERN_DASHBOARD\",includeDemoData:false){message}}"}'
  

# prepare payload for customising the menu
PUBLIC_MENU='[{\\\"label\\\":\\\"Home\\\",\\\"href\\\":\\\"./cranio-provider\\\",\\\"key\\\":\\\"ADmWCg\\\",\\\"submenu\\\":[],\\\"role\\\":\\\"Viewer\\\"},{\\\"label\\\":\\\"Tables\\\",\\\"href\\\":\\\"tables\\\",\\\"role\\\":\\\"Viewer\\\",\\\"key\\\":\\\"BKhvh4\\\",\\\"submenu\\\":[]},{\\\"label\\\":\\\"Schema\\\",\\\"href\\\":\\\"schema\\\",\\\"role\\\":\\\"Manager\\\",\\\"key\\\":\\\"kIhrXl\\\",\\\"submenu\\\":[]},{\\\"label\\\":\\\"Up/Download\\\",\\\"href\\\":\\\"updownload\\\",\\\"role\\\":\\\"Editor\\\",\\\"key\\\":\\\"kwDYFO\\\",\\\"submenu\\\":[]},{\\\"label\\\":\\\"Graphql\\\",\\\"href\\\":\\\"graphql-playground\\\",\\\"role\\\":\\\"Viewer\\\",\\\"key\\\":\\\"8zqR5w\\\",\\\"submenu\\\":[]},{\\\"label\\\":\\\"Settings\\\",\\\"href\\\":\\\"settings\\\",\\\"role\\\":\\\"Manager\\\",\\\"key\\\":\\\"IjJH9y\\\",\\\"submenu\\\":[]},{\\\"label\\\":\\\"Help\\\",\\\"href\\\":\\\"docs\\\",\\\"role\\\":\\\"Viewer\\\",\\\"key\\\":\\\"JtQRmJ\\\",\\\"submenu\\\":[]}]'
 
PROVIDER_MENU='[{\\\"label\\\":\\\"Home\\\",\\\"href\\\":\\\"./cranio-provider\\\",\\\"key\\\":\\\"WRsCIb\\\",\\\"submenu\\\":[],\\\"role\\\":\\\"Viewer\\\"},{\\\"label\\\":\\\"Tables\\\",\\\"href\\\":\\\"tables\\\",\\\"role\\\":\\\"Viewer\\\",\\\"key\\\":\\\"88rTRO\\\",\\\"submenu\\\":[]},{\\\"label\\\":\\\"Schema\\\",\\\"href\\\":\\\"schema\\\",\\\"role\\\":\\\"Manager\\\",\\\"key\\\":\\\"Na6I36\\\",\\\"submenu\\\":[]},{\\\"label\\\":\\\"Up/Download\\\",\\\"href\\\":\\\"updownload\\\",\\\"role\\\":\\\"Editor\\\",\\\"key\\\":\\\"5LQfAo\\\",\\\"submenu\\\":[]},{\\\"label\\\":\\\"Graphql\\\",\\\"href\\\":\\\"graphql-playground\\\",\\\"role\\\":\\\"Viewer\\\",\\\"key\\\":\\\"Z92JNU\\\",\\\"submenu\\\":[]},{\\\"label\\\":\\\"Settings\\\",\\\"href\\\":\\\"settings\\\",\\\"role\\\":\\\"Manager\\\",\\\"key\\\":\\\"p52VMF\\\",\\\"submenu\\\":[]},{\\\"label\\\":\\\"Help\\\",\\\"href\\\":\\\"docs\\\",\\\"role\\\":\\\"Viewer\\\",\\\"key\\\":\\\"BNvx4N\\\",\\\"submenu\\\":[]}]' 
  
# update the navlinks
curl -s "${HOST}/CranioStats/api/graphql" \
  -H "Content-Type: application/json" \
  -H "x-molgenis-token:${TOKEN}" \
  -d '{"query": "mutation{change(settings:[{key:\"menu\",value:\"'${PUBLIC_MENU}'\"}]){message}}"}'

  
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
  
  # create empty schema with provider identifier
  curl -s "${HOST}/api/graphql" \
    -H "Content-Type: application/json" \
    -H "x-molgenis-token:${TOKEN}" \
    -d '{"query":"mutation{createSchema(name:\"'${SCHEMA}'\",description:\"'${NAME}'\"){ message }}"}'

  # make the schema public (for now)
  curl -s "${HOST}/${SCHEMA}/api/graphql" \
    -H "Content-Type: application/json" \
    -H "x-molgenis-token:${TOKEN}" \
    -d '{"query": "mutation{change(members:[{email:\"anonymous\",role:\"Viewer\"}]){message}}"}'

  # update the navlinks
  curl -s "${HOST}/${SCHEMA}/api/graphql" \
    -H "Content-Type: application/json" \
    -H "x-molgenis-token:${TOKEN}" \
    -d '{"query": "mutation{change(settings:[{key:\"menu\",value:\"'${PROVIDER_MENU}'\"}]){message}}"}'

  ((INDEX++))
done

