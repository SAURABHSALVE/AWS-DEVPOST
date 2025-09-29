#!/usr/bin/env python3
"""
Simple HTTP server to serve the frontend files
"""
import http.server
import socketserver
import os
import sys
from pathlib import Path

# Change to the Frontend directory
frontend_dir = Path(__file__).parent
os.chdir(frontend_dir)

PORT = 3000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers to allow backend communication
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.end_headers()

if __name__ == "__main__":
    try:
        with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
            print(f"🚀 Frontend server starting...")
            print(f"📱 Frontend URL: http://localhost:{PORT}")
            print(f"🔗 Test Connection: http://localhost:{PORT}/test-connection.html")
            print(f"🏠 Home Page: http://localhost:{PORT}/index.html")
            print(f"📝 Content Brief: http://localhost:{PORT}/pages/content-brief.html")
            print(f"📚 Content History: http://localhost:{PORT}/pages/content-history.html")
            print(f"\n💡 Make sure the backend is running on http://localhost:8080")
            print(f"⏹️  Press Ctrl+C to stop the server\n")
            
            httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n🛑 Frontend server stopped")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)