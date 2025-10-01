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

    def list_transactions(self):
        """List all transactions."""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        # Example transactions dictionary
        transactions = {
            "1": {"id": "1", "amount": 6000, "to": "Jane Smith", "date": "2025-01-15 17:21:35"},
            "2": {"id": "2", "amount": 5000, "to": "John Doe", "date": "2025-01-16 10:00:00"}
        }
        self.wfile.write(json.dumps(list(transactions.values())).encode())

def run_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, RequestHandler)
    print("Starting httpd on port 8000...")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()