#!/usr/bin/env python3
import json
import time
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from pymongo import MongoClient
from datetime import datetime, timedelta

MONGO_URL = os.environ.get("MONGO_URL")
client = MongoClient(MONGO_URL)
db = client["ilia_chat"]
collection = db["messages"]

def get_messages():
    cutoff = datetime.utcnow() - timedelta(hours=24)
    msgs = list(collection.find(
        {"created_at": {"$gt": cutoff}},
        {"_id": 0, "created_at": 0}
    ).sort("created_at", 1))
    return msgs

def save_message(sender, text):
    t = time.strftime('%H:%M')
    collection.insert_one({
        "sender": sender,
        "text": text,
        "time": t,
        "created_at": datetime.utcnow()
    })

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
            msgs = get_messages()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(msgs).encode())
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
                save_message(sender, text)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"ok":true}')

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 8888))
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    print(f"ilia_chat running on port {PORT}")
    server.serve_forever()
