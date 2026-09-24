import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from jelly_psiduck.cognition import OpenAICompatibleCognition
from jelly_psiduck.workspace import CognitiveView, FeltExperience


def test_real_http_transport_receives_only_subjective_input():
    captured = []
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            captured.append((self.path, json.loads(self.rfile.read(int(self.headers["Content-Length"])))))
            data = json.dumps({"choices": [{"message": {"content": '{"text":"I wonder what happens next."}'}}]}).encode()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(data)
        def log_message(self, *args):
            pass
    server = HTTPServer(("127.0.0.1", 0), Handler)
    worker = threading.Thread(target=server.serve_forever)
    worker.start()
    try:
        provider = OpenAICompatibleCognition(f"http://127.0.0.1:{server.server_port}/v1", "test-model")
        result = provider.think(CognitiveView((FeltExperience("interoception", "I'm cold."),)))
        assert result.text == "I wonder what happens next."
        assert captured[0][0] == "/v1/chat/completions"
        assert "I'm cold." in captured[0][1]["messages"][0]["content"]
        assert "salience" not in captured[0][1]["messages"][0]["content"]
    finally:
        server.shutdown()
        worker.join()
        server.server_close()
