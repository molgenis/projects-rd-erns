#!/bin/sh
emx2_host=''
user_email=''
user_password=''
primary_schema='CranioStats'

# ////////////////////////////////////////////////////////////////////////////

# Create functions that generate new GraphQL queries
new_signin_query () {
    local email=$1
    local password=$2
    query='mutation {
        signin (email: "'$email'", password: "'$password'") {
            status
            message
            token
        }
    }'
    echo $query
}

new_create_schema_query () {
    local name=$1
    local description=$2
    query='mutation {
        createSchema (name: "'$name'", description: "'$description'") {
            status
            message
        }
    }'
    echo $query
}

new_update_schema_query () {
    local name=$1
    local description=$2
    query='mutation {
        updateSchema (name: "'$name'", description: "'$description'") {
            status
            message
        }
    }'
    echo $query
}

new_delete_schema_query () {
    local id=$1
    query='mutation {
        deleteSchema (id: "'$id'") {
            status
            message
        }
    }'
    echo $query
}

new_change_members_query () {
    local email=$1
    local role=$2
    query='mutation {
        change (members: [{email:"'$email'", role:"'$role'"}]) {
            status
            message
        }
    }'
    echo $query
}

new_change_setting_query () {
    local setting=$1
    local value=$2
    query='mutation {
        change (settings:[{key: "'$setting'", value: '$value'}]) {
            status
            message
        }
    }'
    echo $query
}

new_save_query () {
  local table=$1
  local data=$2
  query='mutation {
    save ('$table': '$data') {
      status
      message
    }
  }'
  echo $query
}

new_update_query () {
  local table=$1
  local data=$2
  query='mutation {
    update ('$table': '$data') {
      status
      message
    }
  }'
  echo $query
}


random_key () {
  local length=${1:-12}
  echo "$(cat /dev/urandom | LC_ALL=C tr -dc 'a-zA-Z0-9' | fold -w $length | head -n 1 )"
}

# ////////////////////////////////////////////////////////////////////////////


# sign in and get token

signin_gql=$(new_signin_query $user_email $user_password)
api_token=$(curl "${emx2_host}/api/graphql" \
    -H "Content-Type: application/json" \
    -d "$(jq -c -n --arg query "$signin_gql" '{"query": $query}')" \
    | grep "token" | tr -d '"' | awk '{print $3}'
)

echo $api_token

#~~~~~~~~~~~~~~
# ~ OPTIONAL ~
# remove existing schemas
declare -a schemas_to_remove=(
  "catalogue-demo"
  "CatalogueOntologies"
  "pet store"
)

for schema in "${schemas_to_remove[@]}"
do
    delete_schema_gql=$(new_delete_schema_query $schema)
    curl -s "${emx2_host}/api/graphql" \
        -H "Content-Type: application/json" \
        -H "x-molgenis-token:${api_token}" \
        -d "$(jq -c -n --arg query "$delete_schema_gql" '{"query": $query}')"
done

# //////////////////////////////////////

# init primary schema - load menu, change membership, add description

# create a schema
curl "${emx2_host}/api/graphql" \
    -H "Content-Type: application/json" \
    -H "x-molgenis-token:${api_token}" \
    -d "$(jq -c -n --arg query 'mutation {
        createSchema (name: "CranioStats", description: "CRANIO Stats", template: "ERN_DASHBOARD") {
            status
            message
        }
    }' '{"query": $query}')"


# update the menu

public_menu=$(jq '.public | map(. + {key: "'$(random_key 7)'"}) | tostring' erns/cranio/emx2_menus.json)
set_menu_gql=$(new_change_setting_query "menu" $public_menu)
menu_payload="$(jq -c -n --arg query "$set_menu_gql" '{"query": $query}')"
echo $menu_payload

curl -s "${emx2_host}/${primary_schema}/api/graphql" \
    -H "Content-Type: application/json" \
    -H "x-molgenis-token:${api_token}" \
    -d $menu_payload


# add anonymous user
add_member_gql=$(new_change_members_query 'anonymous' 'Viewer')
curl "${emx2_host}/${primary_schema}/api/graphql" \
    -H "Content-Type: application/json" \
    -H "x-molgenis-token:${api_token}" \
    -d "$(jq -c -n --arg query "$add_member_gql" '{"query": $query}')"
    
    
# update description
update_desc_gql=$(new_update_schema_query $primary_schema "CRANIO STATS")
curl "${emx2_host}/api/graphql" \
    -H "Content-Type: application/json" \
    -H "x-molgenis-token:${api_token}" \
    -d "$(jq -c -n --arg query "$update_desc_gql" '{"query": $query}')"
    
    
# import data
curl "${emx2_host}/CranioStats/api/excel" \
  -H "Content-Type: multipart/form-data" \
  -H "x-molgenis-token:${api_token}" \
  -F "file=@erns/cranio/cranio_emx2.xlsx"

# //////////////////////////////////////

# create schemas for organisations

organisations_json=erns/cranio/emx2_setup_orgs.json
jq -c '.organisations[]' $organisations_json | while read row; do
    org_id=$(jq '.id' <<< $row | xargs)
    org_name=$(jq '.name' <<< $row | xargs)
    echo "Preparing schema for $org_name ($org_id)...."
    
  
    org_create_schema=$(new_create_schema_query $org_id $org_name)
    org_update_schema=$(new_update_schema_query $org_id $org_name)
    
    resp_org_create=$(curl -s "$emx2_host/api/graphql" \
        -H "Content-Type: application/json" \
        -H "x-molgenis-token:${api_token}" \
        -d "$(jq -c -n --arg query "$org_create_schema" '{"query": $query}')")
        
    create_response=$(jq '.data.createSchema.status' <<< $resp_org_create | xargs)
    echo "\tSchema Created: $create_response"
    if [ "$create_response"=="SUCCESS" ]
    then
        provider_menu=$(jq '.provider | map(. + {key: "'$(random_key 7)'"}) | tostring' erns/cranio/emx2_menus.json)
        org_menu_gql=$(new_change_setting_query "menu" $provider_menu)
        org_menu_payload=$(jq -c -n --arg query "$org_menu_gql" '{"query": $query}')
        
        resp_org_menu=$(curl -s "$emx2_host/$org_id/api/graphql" \
            -H "Content-Type: application/json" \
            -H "x-molgenis-token:${api_token}" \
            -d $org_menu_payload)
        menu_response=$(jq '.data.change.status' <<< $resp_org_menu | xargs)
        echo "\tUpdate Menu: $menu_response"
            
        resp_org_member=$(curl -s "$emx2_host/$org_id/api/graphql" \
            -H "Content-Type: application/json" \
            -H "x-molgenis-token:${api_token}" \
            -d "$(jq -c -n --arg query "$add_member_gql" '{"query": $query}')")
        member_response=$(jq '.data.change.status' <<< $resp_org_member | xargs)
        echo "\tUpdate Members: $member_response"
        
        resp_org_update=$(curl -s "$emx2_host/api/graphql" \
            -H "Content-Type: application/json" \
            -H "x-molgenis-token:${api_token}" \
            -d "$(jq -c -n --arg query "$org_update_schema" '{"query": $query}')")
        update_response=$(jq '.data.updateSchema.status' <<< $resp_org_update | xargs)
        echo "\tUpdate Schema: $update_response"
    fi
done


# delete schemas
# jq -c '.organisations[]' $organisations_json | while read row; do
#     org_id=$(jq '.id' <<< $row | xargs)
#     org_name=$(jq '.name' <<< $row | xargs)
#     echo "Preparing to delete schema for $org_name ($org_id)...." 
    
#     org_delete_schema=$(new_delete_schema_query $org_id)
#     resp_org_delete=$(curl -s "$emx2_host/api/graphql" \
#         -H "Content-Type: application/json" \
#         -H "x-molgenis-token:${api_token}" \
#         -d "$(jq -c -n --arg query "$org_delete_schema" '{"query": $query}')")
    
#     response_status=$(jq '.data.deleteSchema.status' <<< $resp_org_delete | xargs)
#     echo "\tStatus: $response_status"
# done        