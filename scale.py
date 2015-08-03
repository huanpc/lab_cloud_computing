import http.client
import json

URI = 'localhost:8080'
header = {'Content-type': 'application/json'}
data = '"instances": "3"'
json_data = json.dumps(data)
method = 'PUT'
link = '/v2/apps/basic-0?force=true'

con = http.client.HTTPConnection(URI)
con.request(method,link,json_data,header)

response = con.getresponse()
print(response.read().decode())
