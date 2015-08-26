import http.client
import json

APP_DEFINE = './demo_web_server.json'
HOST = 'localhost:8080'

data = open(APP_DEFINE)
con = http.client.HTTPConnection(HOST)
header = {'Content-type': 'application/json'}
con.request('POST','/v2/apps',data.read(),header)

response = con.getresponse()
print(response.read().decode())
