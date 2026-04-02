#!/usr/bin/env python3
import json
import time
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

messages = []
OWNER_PASSWORD = "ilia2024"

HTML = open("index.html", "r").read()

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/' or parsed.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML.encode('utf-8'))
        elif parsed.path == '/messages':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(messages).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/send':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
            sender = body.get('sender', 'Unknown')[:30]
            text = body.get('text', '')[:1000].strip()
            if text:
                t = time.strftime('%H:%M')
                messages.append({'sender': sender, 'text': text, 'time': t})
                if len(messages) > 500:
                    messages.pop(0)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"ok":true}')

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 8888))
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    print(f"ilia_chat running on port {PORT}")
    server.serve_forever()
