"""Connection failure checks without requiring a running Ollama service."""

import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from backend.ollama import MODEL, check_connection


class ConnectionTests(unittest.TestCase):
    def check_payload(self, payload):
        with patch("backend.ollama._opener.open", return_value=io.BytesIO(json.dumps(payload).encode())):
            return check_connection()

    def test_installed_model_is_ready(self):
        self.assertEqual(self.check_payload({"models": [{"name": MODEL}]}).state, "ready")

    def test_empty_or_different_model_list_is_missing(self):
        for models in ([], [{"name": "another-model:3b"}]):
            with self.subTest(models=models):
                self.assertEqual(self.check_payload({"models": models}).state, "model_missing")

    def test_malformed_payload_is_not_reported_as_missing_model(self):
        for payload in ([], {}, {"models": None}, {"models": [None]}, {"models": [{"name": 3}]}):
            with self.subTest(payload=payload):
                self.assertEqual(self.check_payload(payload).state, "invalid_response")

    def test_invalid_json_is_handled(self):
        with patch("backend.ollama._opener.open", return_value=io.BytesIO(b"not json")):
            self.assertEqual(check_connection().state, "invalid_response")

    def test_service_failure_is_handled(self):
        for error in (URLError(ConnectionRefusedError()), HTTPError("local", 503, "Unavailable", {}, None)):
            with self.subTest(error=error), patch("backend.ollama._opener.open", side_effect=error):
                self.assertEqual(check_connection().state, "unavailable")

    def test_direct_and_wrapped_timeouts_are_handled(self):
        for error in (TimeoutError(), URLError(TimeoutError())):
            with self.subTest(error=error), patch("backend.ollama._opener.open", side_effect=error):
                self.assertEqual(check_connection().state, "timeout")


if __name__ == "__main__":
    unittest.main()
