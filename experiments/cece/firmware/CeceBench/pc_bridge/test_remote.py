"""Contract tests for the laptop-to-robot LAN message client."""
import base64
import itertools
import json
import struct
import threading
from types import SimpleNamespace
from unittest.mock import patch
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
import laptop_voice

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        body = self.rfile.read(int(self.headers['Content-Length']))
        if self.path not in ('/message', '/speaker') or self.headers.get('X-Cece-Token') != 'test-only-12345678':
            self.send_error(403)
            return
        self.server.last_message = body
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Message accepted; OLED output not verified')
    def do_GET(self):
        if self.path not in ('/microphone', '/status') or self.headers.get('X-Cece-Token') != 'test-only-12345678':
            self.send_error(403)
            return
        if self.path == '/status':
            data = b'{"range_cm":42.5,"oled_detected":true}'
            self.send_response(200)
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        self.server.reads += 1
        value = 1000 if self.server.reads <= 3 else 0
        pcm = struct.pack('<h', value) * 4096
        self.send_response(200)
        self.send_header('Content-Length', str(len(pcm)))
        self.end_headers()
        self.wfile.write(pcm)
    def log_message(self, *args):
        pass

class RemoteTests(unittest.TestCase):
    def test_sends_authenticated_message(self):
        server = HTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            result = laptop_voice.send_robot_message(f'http://127.0.0.1:{server.server_port}', 'test-only-12345678', 'Hello Cece')
            self.assertIn('accepted', result)
            self.assertEqual(server.last_message, b'Hello Cece')
        finally:
            server.shutdown()
            server.server_close()
            thread.join()
    def test_robot_mic_chunks_are_transcribed(self):
        server = HTTPServer(('127.0.0.1', 0), Handler)
        server.reads = 0
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        model = SimpleNamespace(transcribe=lambda audio, **kwargs: (iter([SimpleNamespace(text=' hello cece ')]), None))
        ticks = itertools.count()
        try:
            with patch.object(laptop_voice, 'time', SimpleNamespace(monotonic=lambda: next(ticks) * 0.3)):
                text, peak = laptop_voice.record_robot(model, f'http://127.0.0.1:{server.server_port}', 'test-only-12345678', whisper=True)
            self.assertEqual((text, peak), ('hello cece', 1000))
            self.assertGreater(server.reads, 3)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_robot_status_and_speaker_transport(self):
        server = HTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        url, token = f'http://127.0.0.1:{server.server_port}', 'test-only-12345678'
        try:
            reading = json.loads(laptop_voice.robot_request(url, token, '/status'))
            self.assertEqual(reading['range_cm'], 42.5)
            pcm = struct.pack('<hhhh', 0, 123, -456, 0)
            laptop_voice.robot_request(url, token, '/speaker', base64.b64encode(pcm))
            self.assertEqual(base64.b64decode(server.last_message), pcm)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_rejects_invalid_configuration(self):
        with self.assertRaises(ValueError):
            laptop_voice.send_robot_message('http://localhost', 'short', 'hello')
        with self.assertRaises(ValueError):
            laptop_voice.send_robot_message('http://example.com/path', 'test-only-12345678', 'hello')
        with self.assertRaises(ValueError):
            laptop_voice.send_robot_message('http://localhost', 'test-only-12345678', 'x' * 121)

if __name__ == '__main__':
    unittest.main()
