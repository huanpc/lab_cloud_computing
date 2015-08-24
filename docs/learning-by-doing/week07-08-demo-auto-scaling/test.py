
from http.server import BaseHTTPRequestHandler, HTTPServer

hostName = "0.0.0.0"
hostPort = 8084

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>DEMO WEB SERVER</title></head>", "utf-8"))
        self.wfile.write(bytes("<body><p>HELLO WORLD!!</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))

myServer = HTTPServer((hostName, hostPort), MyServer)
myServer.serve_forever()




