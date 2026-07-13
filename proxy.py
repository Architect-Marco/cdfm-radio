
# proxy.py
import http.server
import urllib.request
import json
import sys

PORT = 5001
# Replace this with your actual Hugging Face token (e.g., "hf_...")
HF_TOKEN = "YOUR_HUGGING_FACE_TOKEN_HERE" 

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_POST(self):
        if self.path == "/generate":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Forward the request to Hugging Face using Python's modern SSL stack
            hf_url = "https://api-inference.huggingface.co/models/facebook/musicgen-small"
            
            req = urllib.request.Request(
                hf_url,
                data=post_data,
                headers={
                    "Authorization": f"Bearer {HF_TOKEN}",
                    "Content-Type": "application/json"
                },
                method="POST"
            )
            
            try:
                with urllib.request.urlopen(req) as response:
                    self.send_response(200)
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Content-Type', 'audio/wav')
                    self.end_headers()
                    self.wfile.write(response.read())
            except urllib.error.HTTPError as e:
                error_data = e.read()
                self.send_response(e.code)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(error_data)
            except Exception as e:
                self.send_response(500)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(str(e).encode())

if __name__ == "__main__":
    if HF_TOKEN == "YOUR_HUGGING_FACE_TOKEN_HERE":
        print("[ERROR] Please add your actual Hugging Face Token to proxy.py")
        sys.exit(1)
        
    server = http.server.HTTPServer(('127.0.0.1', PORT), ProxyHandler)
    print(f"📡 Sovereign Grid Proxy active on http://127.0.0.1:{PORT}")
    server.serve_forever()
