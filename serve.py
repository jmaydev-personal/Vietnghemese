#!/usr/bin/env python3
"""
Vietnghemese - Local Word Audio Server
Run: python3 serve.py
Then open http://localhost:8765 in your browser (or on mobile: http://YOUR_IP:8765)
"""

import http.server
import socketserver
import os
import socket

PORT = 8765
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(SCRIPT_DIR, 'audio')
INDEX_FILE = os.path.join(SCRIPT_DIR, 'index.html')


def get_local_ip():
    """Get the local network IP for mobile access."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"


class Handler(http.server.BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        pass  # Suppress request logs for cleaner output

    def send_file(self, path, content_type):
        try:
            with open(path, 'rb') as f:
                data = f.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'public, max-age=86400')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(data)
        except FileNotFoundError:
            self.send_error(404, f"Not found: {path}")

    def do_GET(self):
        path = self.path.split('?')[0]  # Strip query strings

        if path == '/' or path == '/index.html':
            self.send_file(INDEX_FILE, 'text/html; charset=utf-8')

        elif path == '/words.json':
            self.send_file(os.path.join(SCRIPT_DIR, 'words.json'), 'application/json; charset=utf-8')

        elif path.startswith('/audio/'):
            filename = path[len('/audio/'):]
            # Security: only allow fptai-*.mp3 filenames
            if filename.startswith('fptai-') and filename.endswith('.mp3') and '/' not in filename and '..' not in filename:
                audio_path = os.path.join(AUDIO_DIR, filename)
                self.send_file(audio_path, 'audio/mpeg')
            else:
                self.send_error(403, "Forbidden")

        else:
            self.send_error(404, "Not found")


if __name__ == '__main__':
    local_ip = get_local_ip()

    print()
    print("  🇻🇳  Vietnghemese - Vietnamese Word Player")
    print("  " + "─" * 40)
    print(f"  Local:   http://localhost:{PORT}")
    print(f"  Mobile:  http://{local_ip}:{PORT}")
    print()
    print("  Open either URL in your browser.")
    print("  Make sure your phone is on the same Wi-Fi network.")
    print()
    print("  Press Ctrl+C to stop.")
    print()

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.allow_reuse_address = True
        httpd.serve_forever()
