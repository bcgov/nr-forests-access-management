"""Exercise the real HTTP preflight checker against a local test server."""

import subprocess
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

from check_admin_api_preflight import check_preflight


ORIGIN = "https://frontend.example"
GOOD_HEADERS = [
    ("Access-Control-Allow-Origin", ORIGIN),
    ("Access-Control-Allow-Methods", "OPTIONS, GET, POST"),
    ("Access-Control-Allow-Headers", "Authorization, Content-Type"),
]


class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.server.observed = (self.path, dict(self.headers))
        self.send_response(self.server.response_status)
        for name, value in self.server.response_headers:
            self.send_header(name, value)
        self.end_headers()

    def log_message(self, *args):
        pass


class PreflightTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}/admin-user-accesses"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.server.response_status = 200
        self.server.response_headers = GOOD_HEADERS.copy()

    def test_sends_the_browser_preflight_without_credentials(self):
        check_preflight(self.url, ORIGIN + "/callback?example=1")
        path, headers = self.server.observed
        self.assertEqual(path, "/admin-user-accesses")
        self.assertEqual(headers["Origin"], ORIGIN)
        self.assertEqual(headers["Access-Control-Request-Method"], "GET")
        self.assertEqual(headers["Access-Control-Request-Headers"], "authorization,content-type")
        self.assertNotIn("Authorization", headers)
        self.assertNotIn("Cookie", headers)

    def test_accepts_current_gateway_wildcard_origin_and_204(self):
        self.server.response_status = 204
        self.server.response_headers[0] = ("Access-Control-Allow-Origin", "*")
        check_preflight(self.url, ORIGIN)

    def test_accepts_case_insensitive_and_split_header_names(self):
        self.server.response_headers = GOOD_HEADERS[:2] + [
            ("access-control-allow-headers", " AUTHORIZATION "),
            ("Access-Control-Allow-Headers", "content-type"),
        ]
        check_preflight(self.url, ORIGIN)

    def test_accepts_wildcards_only_with_explicit_authorization(self):
        self.server.response_headers = [
            ("Access-Control-Allow-Origin", "*"),
            ("Access-Control-Allow-Methods", "*"),
            ("Access-Control-Allow-Headers", "Authorization, *"),
        ]
        check_preflight(self.url, ORIGIN)

    def test_rejects_http_errors_and_redirects(self):
        for status in [301, 302, 307, 401, 403, 404, 500, 502]:
            with self.subTest(status=status):
                self.server.response_status = status
                self.server.response_headers = GOOD_HEADERS + [("Location", self.url)]
                with self.assertRaises(HTTPError):
                    check_preflight(self.url, ORIGIN)

    def test_rejects_200_responses_with_invalid_cors(self):
        cases = {
            "missing origin": GOOD_HEADERS[1:],
            "wrong origin": [("Access-Control-Allow-Origin", "https://other.example")] + GOOD_HEADERS[1:],
            "duplicate origin": GOOD_HEADERS + [GOOD_HEADERS[0]],
            "missing methods": [GOOD_HEADERS[0], GOOD_HEADERS[2]],
            "wrong method": [GOOD_HEADERS[0], ("Access-Control-Allow-Methods", "POST, TARGET"), GOOD_HEADERS[2]],
            "missing headers": GOOD_HEADERS[:2],
            "missing authorization": GOOD_HEADERS[:2] + [("Access-Control-Allow-Headers", "Content-Type")],
            "authorization is not wildcarded": GOOD_HEADERS[:2] + [("Access-Control-Allow-Headers", "*")],
            "missing content type": GOOD_HEADERS[:2] + [("Access-Control-Allow-Headers", "Authorization")],
        }
        for name, headers in cases.items():
            with self.subTest(name=name):
                self.server.response_headers = headers
                with self.assertRaises(ValueError):
                    check_preflight(self.url, ORIGIN)

    def test_timeout_is_bounded(self):
        with patch("check_admin_api_preflight.urlopen", side_effect=TimeoutError) as opener:
            with self.assertRaises(TimeoutError):
                check_preflight(self.url, ORIGIN)
            self.assertEqual(opener.call_args.kwargs["timeout"], 30)

    def test_cli_exit_status_controls_workflow_success(self):
        checker = Path(__file__).with_name("check_admin_api_preflight.py")
        cases = [(200, GOOD_HEADERS, 0), (500, GOOD_HEADERS, 1), (200, GOOD_HEADERS[:2], 1)]
        for status, headers, expected_exit in cases:
            with self.subTest(status=status, expected_exit=expected_exit):
                self.server.response_status = status
                self.server.response_headers = headers
                result = subprocess.run(
                    [sys.executable, str(checker), self.url, ORIGIN],
                    capture_output=True, text=True, timeout=10,
                )
                self.assertEqual(result.returncode, expected_exit, result.stderr)


if __name__ == "__main__":
    unittest.main()
