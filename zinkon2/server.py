from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver
import json
from zinkon2 import get_move

class MyHandler(BaseHTTPRequestHandler):
	def do_OPTIONS(self):
		self.send_response(200, "ok")
		self.send_header('Access-Control-Allow-Origin', '*')
		self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
		self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
		self.send_header("Access-Control-Allow-Headers", "Content-Type")
		self.send_header("Access-Control-Allow-Headers", "access-control-allow-origin")
		self.end_headers()

	def do_POST(self):
		content_len = int(self.headers.get('content-length'))
		post_body_json = self.rfile.read(content_len)
		input = json.loads(post_body_json)
		self.send_response(200)
		self.send_header('Access-Control-Allow-Origin', '*')
		self.send_header('Content-Type', 'application/json')
		self.end_headers()
		move = get_move(input)
		response = '{"move":"%s"}' % move
		self.wfile.write(response.encode('UTF-8'))

if __name__ == '__main__':
	httpd = HTTPServer(('', 8000), MyHandler)
	print('serving')
	httpd.serve_forever()