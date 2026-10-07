# Tiny local server for tools/globe-story.html?record=1: serves the project and saves the posted frames.
#   python3 tools/frame-server.py <frames dir>   then open http://localhost:8091/tools/globe-story.html?record=1
import sys, os, http.server, urllib.parse
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
class H(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        i = int(urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)["i"][0])
        open(os.path.join(OUT, f"f{i:04d}.png"), "wb").write(self.rfile.read(int(self.headers["Content-Length"])))
        self.send_response(204); self.end_headers()
    def log_message(self, *a): pass
os.chdir(os.path.join(os.path.dirname(__file__), ".."))
http.server.ThreadingHTTPServer(("127.0.0.1", 8091), H).serve_forever()
