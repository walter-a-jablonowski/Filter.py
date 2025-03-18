import http.server
import socketserver
import json
import os
import sys
from urllib.parse import urlparse, parse_qs
from Filter import Filter

class FilterHandler(http.server.SimpleHTTPRequestHandler):
  def do_GET(self):
    # Serve static files
    self.path = self.path.split('?')[0]  # Remove query parameters
    
    if self.path == '/':
      self.path = '/index.html'
    
    try:
      # Try to serve the file
      return http.server.SimpleHTTPRequestHandler.do_GET(self)
    except:
      # If file not found, return 404
      self.send_response(404)
      self.end_headers()
      self.wfile.write(b'File not found')
  
  def do_POST(self):
    # Handle AJAX requests
    if self.path == '/ajax':
      content_length = int(self.headers['Content-Length'])
      post_data = self.rfile.read(content_length)
      
      try:
        input_data = json.loads(post_data.decode('utf-8'))
        
        if 'filter' not in input_data or 'mode' not in input_data:
          self.send_error(400, 'Invalid request')
          return
        
        # Initialize filter with synonyms file
        filter_obj = Filter('synonyms.yml')
        tree = filter_obj.parse(input_data['filter'])
        
        if input_data['mode'] == 'text':
          if 'input' not in input_data:
            self.send_error(400, 'No input text provided')
            return
          
          result = filter_obj.check(input_data['input'], tree)
          response = {'result': result}
          
        elif input_data['mode'] == 'records':
          if 'records' not in input_data or not isinstance(input_data['records'], list):
            self.send_error(400, 'No records provided')
            return
          
          results = []
          for record in input_data['records']:
            record['result'] = filter_obj.check(record, tree)
            results.append(record)
          
          response = {'results': results}
          
        else:
          self.send_error(400, 'Invalid mode')
          return
        
        # Send response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))
        
      except Exception as e:
        self.send_error(500, str(e))
    else:
      self.send_error(404, 'Not found')

def run_server(port=8000):
  # Change to the directory of this script
  os.chdir(os.path.dirname(os.path.abspath(__file__)))
  
  # Create server
  handler = FilterHandler
  httpd = socketserver.TCPServer(("", port), handler)
  
  print(f"Server running at http://localhost:{port}/")
  httpd.serve_forever()

if __name__ == "__main__":
  port = 8000
  if len(sys.argv) > 1:
    try:
      port = int(sys.argv[1])
    except ValueError:
      print(f"Invalid port: {sys.argv[1]}")
      sys.exit(1)
  
  run_server(port)