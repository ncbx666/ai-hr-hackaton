import http.server
import socketserver
import os

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

if __name__ == "__main__":
    PORT = 8002
    os.chdir(r"C:\Users\79046\Desktop\ai-hr-hackaton\ai-hr-hackaton")
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"🌐 HTTP сервер запущен на порту {PORT}")
        print(f"📄 Открыть: http://localhost:{PORT}/websocket_test.html")
        httpd.serve_forever()
