from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import urlparse, parse_qs
from typing import Any
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dsa.parse import TransactionMessages, get_messages

class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        """Handle GET requests."""
        url_parts = urlparse(self.path)
        if url_parts.path == "/transactions":
            self.list_transactions()
        elif url_parts.path.startswith("/transactions/"):
            self.view_transaction(url_parts.path.split("/")[-1])
        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def do_POST(self):
        """Handle POST requests."""
        url_parts = urlparse(self.path)
        if url_parts.path == "/transactions":
            self.add_transaction()
        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def do_PUT(self):
        """Handle PUT requests."""
        url_parts = urlparse(self.path)
        if url_parts.path.startswith("/transactions/"):
            self.update_transaction(url_parts.path.split("/")[-1])
        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def do_DELETE(self):
        """Handle DELETE requests."""
        url_parts = urlparse(self.path)
        if url_parts.path.startswith("/transactions/"):
            self.delete_transaction(url_parts.path.split("/")[-1])
        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def list_transactions(self):
        """List all transactions."""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(list(transactions.values())).encode())

    def view_transaction(self, transaction_id):
        """View one transaction."""
        if transaction_id in transactions:
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(transactions[transaction_id]).encode())
        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def add_transaction(self):
        """Add a new transaction."""
        content_length = int(self.headers['Content-Length'])
        post_body = self.rfile.read(content_length)
        try:
            new_transaction = json.loads(post_body.decode())
            new_transaction_id = str(len(transactions) + 1)
            transactions[new_transaction_id] = {"id": new_transaction_id, **new_transaction}
            self.send_response(201)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(transactions[new_transaction_id]).encode())
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())

    def update_transaction(self, transaction_id):
        """Update an existing transaction."""
        if transaction_id in transactions:
            content_length = int(self.headers['Content-Length'])
            post_body = self.rfile.read(content_length)
            try:
                updated_transaction = json.loads(post_body.decode())
                transactions[transaction_id].update(updated_transaction)
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(transactions[transaction_id]).encode())
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def delete_transaction(self, transaction_id):
        """Delete a transaction."""
        if transaction_id in transactions:
            del transactions[transaction_id]
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"message": "Transaction deleted"}).encode())
        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

def run_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, RequestHandler)
    print("Starting httpd on port 8000...")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()