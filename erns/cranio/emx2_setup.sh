#!/bin/sh
emx2_host=''
user_email=''
user_password=''
target_schema='cli_schema_test'

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
        createSchema (name: "'$name'", description: "'$description'") {
            status
            message
        }
    }'
    echo $query
}

new_delete_schema_query () {
    local name=$1
    query='mutation {
        deleteSchema (name: "'$name'") {
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
  delete_schema_gql=$(new_delete_schema_query $SCHEMA)
    curl -s "${emx2_host}/api/graphql" \
        -H "x-molgenis-token:${api_token}" \
        -H "Content-Type: application/json" \
        -d "$(jq -c -n --arg query "$delete_schema_gql" '{"query": $query}')"
done
#~~~~~~~~~~~~~~
  

# create a schema
create_schema_gql=$(new_create_schema_query $target_schema "created by curl")
curl "${emx2_host}/api/graphql" \
    -H "x-molgenis-token:${api_token}" \
    -H "Content-Type: application/json" \
    -d "$(jq -c -n --arg query "$create_schema_gql" '{"query": $query}')"


# update the menu
public_menu=$(jq '.public | tostring' erns/cranio/emx2_menus.json)
set_menu_gql=$(new_change_setting_query "menu" $public_menu)
menu_payload="$(jq -c -n --arg query "$set_menu_gql" '{"query": $query}')"
echo $menu_payload
 
curl -s "${emx2_host}/${target_schema}/api/graphql" \
    -H "Content-Type: application/json" \
    -H "x-molgenis-token:${api_token}" \
    -d $menu_payload



# add anonymous user
add_member_gql=$(new_change_members_query 'anonymous' 'Viewer')
curl "${emx2_host}/${target_schema}/api/graphql" \
    -H "x-molgenis-token:${api_token}" \
    -H "Content-Type: application/json" \
    -d "$(jq -c -n --arg query "$add_member_gql" '{"query": $query}')"