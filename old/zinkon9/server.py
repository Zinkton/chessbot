from functools import partial
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import argparse
from chess_bot import ChessBot


class MyHandler(BaseHTTPRequestHandler):
    def __init__(self, chess_bot, *args, **kwargs):
        self.chess_bot = chess_bot

        super().__init__(*args, **kwargs)

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods',
                            'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers",
                            "X-Requested-With")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Headers",
                            "access-control-allow-origin")
        self.end_headers()

    def do_POST(self):
        content_len = int(self.headers.get('content-length'))
        post_body_json = self.rfile.read(content_len)
        input = json.loads(post_body_json)
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        move = self.chess_bot.get_move(input)
        response = '{"move":"%s"}' % move
        self.wfile.write(response.encode('UTF-8'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HTTP Server for Chess Bot')
    parser.add_argument('--port', type=int, default=8000, help='Port to run the HTTP server on (default: 8000)')
    args = parser.parse_args()

    chess_bot = ChessBot()
    handler_with_chess_bot = partial(MyHandler, chess_bot)
    
    port = args.port
    httpd = HTTPServer(('', port), handler_with_chess_bot)
    print(f'Serving on port {port}')
    httpd.serve_forever()
