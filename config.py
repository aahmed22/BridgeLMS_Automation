base_url = 'ENTER BASE URL'

authToken = 'ENTER AUTH TOKEN'

headers = {
    'Authorization': 'Basic {0}'.format(authToken)
}

#ENTER THE NAME OF THE RELATED OBJECTS YOU WANT TO ACQUIRE INFO FROM IN THE PAYLOAD
payload = {"only":["OBJECT1","OBJECT2","OBJECT3","OBJECT4","OBJECT5"]}

file_name = 'bridge_data_dump.zip'

# Example of Postgres connection 'postgresql://db_username:db_passwd@server_endpoint_name:5432/db_name'
psql_string = 'ENTER POSTGRES ENDPOINT CONNECTION'
