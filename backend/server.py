import http.server
import json
import os
import mimetypes
import re
from email.parser import BytesParser
from email.policy import default

from backend.utilities.text_extractor import extract_text_from_bytes
from backend.analysis.pipeline import run_analysis_pipeline

PORT = 8000
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
frontend_dir = os.path.join(project_root, "frontend")

class TruthLensHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        # Log requests to console cleanly
        print(f"INFO: {self.client_address[0]} - {format%args}")

    def end_headers(self):
        # Inject standard headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

    def do_OPTIONS(self):
        # Handle browser preflight CORS checks
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        # Routings to serve the frontend single-page dashboard
        if self.path == "/" or self.path == "/index.html" or self.path == "":
            self.serve_file(os.path.join(project_root, "index.html"))
        elif self.path.startswith("/frontend/"):
            # Strip prefix to locate files in the frontend workspace relatively
            rel_path = self.path[len("/frontend/"):]
            
            # Normalize path to protect against directory traversal attacks
            normalized_rel = os.path.normpath(rel_path)
            if normalized_rel.startswith("..") or os.path.isabs(normalized_rel):
                self.send_error(400, "Invalid static path request")
                return
                
            file_path = os.path.join(frontend_dir, normalized_rel)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                self.serve_file(file_path)
            else:
                self.send_error(404, "File Not Found")
        else:
            self.send_error(404, "Not Found")

    def serve_file(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            
            # Resolve content-type headers
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = 'application/octet-stream'
                
            self.send_header('Content-Type', mime_type)
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Server error reading static content: {str(e)}")

    def do_POST(self):
        if self.path == "/api/analyze":
            self.handle_analyze()
        else:
            self.send_error(404, "Not Found")

    def handle_analyze(self):
        content_type = self.headers.get('Content-Type')
        content_length = int(self.headers.get('Content-Length', 0))
        
        if not content_type or not content_type.startswith('multipart/form-data'):
            self.send_json_error(400, "Request must be multipart/form-data")
            return
            
        try:
            body_bytes = self.rfile.read(content_length)
        except Exception as e:
            self.send_json_error(400, f"Failed to read post body: {str(e)}")
            return

        # Parse multipart form data using standard email parser libraries (Python 3.13 compliant)
        try:
            header_prefix = f"Content-Type: {content_type}\r\n\r\n".encode('utf-8')
            full_msg_bytes = header_prefix + body_bytes
            msg = BytesParser(policy=default).parsebytes(full_msg_bytes)
            
            text_data = ""
            file_bytes = None
            file_name = ""
            
            if msg.is_multipart():
                for part in msg.iter_parts():
                    disposition = part.get('Content-Disposition', '')
                    # Extract parameter fields using standard regex
                    name_match = re.search(r'name="([^"]+)"', disposition)
                    if not name_match:
                        continue
                    field_name = name_match.group(1)
                    
                    if field_name == 'text':
                        text_data = part.get_content().strip()
                    elif field_name == 'file':
                        filename_match = re.search(r'filename="([^"]+)"', disposition)
                        if filename_match:
                            file_name = filename_match.group(1)
                            file_bytes = part.get_payload(decode=True)
                            
            document_text = ""
            if file_bytes and file_name:
                try:
                    document_text = extract_text_from_bytes(file_bytes, file_name)
                except ValueError as ve:
                    self.send_json_error(400, str(ve))
                    return
            elif text_data:
                document_text = text_data
            else:
                self.send_json_error(400, "No legal document provided. Paste text or upload a file.")
                return
                
            if not document_text.strip() or len(document_text.strip()) < 50:
                self.send_json_error(400, "Document too short. Paste text or upload a file (minimum 50 characters).")
                return

            # Process the clean text document pipeline
            report = run_analysis_pipeline(document_text)
            
            # Send JSON response
            response_data = json.dumps(report).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(response_data))
            self.end_headers()
            self.wfile.write(response_data)
            
        except Exception as e:
            self.send_json_error(500, f"Error running risk analyzer pipeline: {str(e)}")

    def send_json_error(self, status_code, message):
        response_content = json.dumps({"detail": message}).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(response_content))
        self.end_headers()
        self.wfile.write(response_content)

def run():
    print(f"INFO: TruthLens AI server starting on http://127.0.0.1:{PORT}")
    server_address = ('127.0.0.1', PORT)
    httpd = http.server.HTTPServer(server_address, TruthLensHTTPRequestHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nINFO: Server shutting down...")
        httpd.server_close()

if __name__ == '__main__':
    run()