#!/usr/bin/env python3
"""
Plain-Python REST API using http.server
Supports:
  GET /transactions
  GET /transactions/{id}
  POST /transactions
  PUT /transactions/{id}
  DELETE /transactions/{id}
Basic Authentication: username=admin password=password (default)
Data persisted to data/transactions.json
"""

import json
import base64
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import re

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'transactions.json')
USERNAME = "admin"
PASSWORD = "password"
PORT = 8000

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

class SimpleJSONHandler(BaseHTTPRequestHandler):
    server_version = "MoMoDataHub/0.1"

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="MoMo API"')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'error': 'Authentication required'}).encode('utf-8'))

    def authenticate(self):
        auth = self.headers.get('Authorization')
        if not auth or not auth.startswith('Basic '):
            return False
        try:
            token = auth.split(' ', 1)[1].strip()
            decoded = base64.b64decode(token).decode('utf-8')
            username, password = decoded.split(':', 1)
            return username == USERNAME and password == PASSWORD
        except Exception:
            return False

    def parse_path(self):
        # returns (resource, id_or_none)
        path = urlparse(self.path).path
        m = re.match(r'^/transactions(?:/([^/]+))?/?$', path)
        if m:
            return ('transactions', m.group(1))
        return (None, None)

    def send_json(self, data, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        if data is None:
            return
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def do_GET(self):
        if not self.authenticate():
            return self.do_AUTHHEAD()
        resource, rid = self.parse_path()
        if resource != 'transactions':
            return self.send_json({'error': 'Not Found'}, code=404)
        data = load_data()
        if rid is None:
            return self.send_json(data)
        # find by id (string or int)
        for t in data:
            if str(t.get('id')) == str(rid):
                return self.send_json(t)
        return self.send_json({'error': 'Transaction not found'}, code=404)

    def do_POST(self):
        if not self.authenticate():
            return self.do_AUTHHEAD()
        resource, rid = self.parse_path()
        if resource != 'transactions' or rid is not None:
            return self.send_json({'error': 'Not Found'}, code=404)
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length) if length else b''
        try:
            payload = json.loads(body.decode('utf-8'))
        except Exception:
            return self.send_json({'error': 'Invalid JSON'}, code=400)

        data = load_data()
        # assign new id
        existing_ids = [int(item.get('id', 0)) for item in data if str(item.get('id', '')).isdigit()]
        new_id = max(existing_ids, default=0) + 1
        payload['id'] = new_id
        data.append(payload)
        save_data(data)
        self.send_json(payload, code=201)

    def do_PUT(self):
        if not self.authenticate():
            return self.do_AUTHHEAD()
        resource, rid = self.parse_path()
        if resource != 'transactions' or rid is None:
            return self.send_json({'error': 'Not Found'}, code=404)
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length) if length else b''
        try:
            payload = json.loads(body.decode('utf-8'))
        except Exception:
            return self.send_json({'error': 'Invalid JSON'}, code=400)

        data = load_data()
        for idx, t in enumerate(data):
            if str(t.get('id')) == str(rid):
                # merge/update
                payload['id'] = int(rid) if str(rid).isdigit() else rid
                data[idx] = payload
                save_data(data)
                return self.send_json(payload)
        return self.send_json({'error': 'Transaction not found'}, code=404)

    def do_DELETE(self):
        if not self.authenticate():
            return self.do_AUTHHEAD()
        resource, rid = self.parse_path()
        if resource != 'transactions' or rid is None:
            return self.send_json({'error': 'Not Found'}, code=404)
        data = load_data()
        new = [t for t in data if str(t.get('id')) != str(rid)]
        if len(new) == len(data):
            return self.send_json({'error': 'Transaction not found'}, code=404)
        save_data(new)
        return self.send_json({'message': 'Deleted'}, code=200)

    def log_message(self, format, *args):
        # reduce verbosity; write to stdout
        print("%s - - [%s] %s" % (self.client_address[0], self.log_date_time_string(), format%args))

def run(server_class=HTTPServer, handler_class=SimpleJSONHandler, port=PORT):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}. Basic Auth user={USERNAME}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down server")
    httpd.server_close()

if __name__ == '__main__':
    run()