import http.client
import json

URI = 'localhost:8080'
header = {'Content-type': 'application/json'}
method = 'GET'
link = '/v2/apps/basic-0'

con = http.client.HTTPConnection(URI)
con.request(method,link,'',header)

response = con.getresponse()
data = json.loads(response.read().decode())
print(data)
