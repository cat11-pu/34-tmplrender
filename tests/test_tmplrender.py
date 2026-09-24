import json
import threading
import unittest
import urllib.error
import urllib.request

from tmplrender import Renderer
from server import serve

class TestRenderer(unittest.TestCase):
    def test_variable_substitution(self):
        self.assertEqual(Renderer().render("hi {{ name }}", {"name": "ann"}), "hi ann")

    def test_missing_variable_is_empty(self):
        self.assertEqual(Renderer().render("hi {{ nope }}", {}), "hi ")

    def test_check_default_shape(self):
        self.assertIn("ok", Renderer().check("plain"))

    def test_stats_shape(self):
        self.assertIn("max_depth", Renderer().stats())

    def test_http_render(self):
        server = serve(0)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = "http://127.0.0.1:%d" % server.server_port
        with urllib.request.urlopen(base + "/render",
                                    data=b'{"template": "{{ a }}", "context": {"a": "x"}}',
                                    timeout=5) as response:
            self.assertEqual(json.loads(response.read())["html"], "x")
        server.shutdown()
