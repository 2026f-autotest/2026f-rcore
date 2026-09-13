"""Exercise provisioning order, retry safety and GitHub API request boundaries."""

import importlib.util
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("enroll", ROOT / "enroll.py")
enroll = importlib.util.module_from_spec(spec)
spec.loader.exec_module(enroll)


class EnrollmentTests(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.endpoint = "repos/2026f-autotest/2026f-rcore-student"
        self.repo = None
        self.variable = None

    def api(self, method, path, data=None, missing_ok=False):
        self.calls.append((method, path, data))
        if path == self.endpoint:
            return self.repo
        if path.endswith("/generate"):
            self.repo = {"id": 123, "private": False,
                         "template_repository": {"full_name": enroll.TEMPLATE}}
            return self.repo
        if "/branches?" in path:
            return [{"name": name} for name in enroll.BRANCHES]
        if path.endswith("/actions/variables/STUDENT_GITHUB"):
            return self.variable
        if path.endswith("/actions/variables"):
            self.variable = data
            return None
        if path.endswith("/repositories/123") or path.endswith("/enable"):
            return None
        if path.endswith("/collaborators/student"):
            return {"id": 456}
        self.fail(f"Unexpected API request: {method} {path}")

    def test_create_all_branches_bind_student_before_inviting(self):
        with patch.object(enroll, "api", side_effect=self.api):
            enroll.enroll({"login": "student"}, {"visibility": "selected"})
        generated = next(call for call in self.calls if call[1].endswith("/generate"))
        self.assertEqual(generated[2]["owner"], "2026f-autotest")
        self.assertTrue(generated[2]["include_all_branches"])
        self.assertFalse(generated[2]["private"])
        self.assertEqual(self.variable, {"name": "STUDENT_GITHUB", "value": "student"})
        self.assertEqual(self.calls[-1], ("PUT", self.endpoint + "/collaborators/student", {"permission": "push"}))
        self.assertTrue(any(call[1].endswith("/repositories/123") for call in self.calls))

    def test_retry_keeps_repository_and_existing_identity(self):
        self.repo = {"id": 123, "private": False,
                     "template_repository": {"full_name": enroll.TEMPLATE}}
        self.variable = {"name": "STUDENT_GITHUB", "value": "student"}
        with patch.object(enroll, "api", side_effect=self.api):
            enroll.enroll({"login": "student"}, {"visibility": "all"})
        self.assertFalse(any(method == "POST" for method, _, _ in self.calls))
        self.assertFalse(any("/secrets/" in path for _, path, _ in self.calls))

    def test_existing_unrelated_repository_is_not_modified(self):
        self.repo = {"id": 123, "private": False}
        with patch.object(enroll, "api", side_effect=self.api), self.assertRaises(ValueError):
            enroll.enroll({"login": "student"}, {"visibility": "selected"})
        self.assertTrue(all(method == "GET" for method, _, _ in self.calls))

    def test_existing_wrong_student_is_not_overwritten_or_invited(self):
        self.repo = {"id": 123, "private": False,
                     "template_repository": {"full_name": enroll.TEMPLATE}}
        self.variable = {"name": "STUDENT_GITHUB", "value": "someone-else"}
        with patch.object(enroll, "api", side_effect=self.api), self.assertRaises(ValueError):
            enroll.enroll({"login": "student"}, {"visibility": "selected"})
        self.assertTrue(all(method == "GET" for method, _, _ in self.calls))

    def test_secret_access_failure_stops_before_invitation(self):
        def fail_secret(method, path, data=None, missing_ok=False):
            if "/secrets/" in path:
                raise RuntimeError("HTTP 403: organization policy")
            return self.api(method, path, data, missing_ok)
        with patch.object(enroll, "api", side_effect=fail_secret), self.assertRaises(RuntimeError):
            enroll.enroll({"login": "student"}, {"visibility": "selected"})
        self.assertFalse(any("/collaborators/" in path for _, path, _ in self.calls))

    def test_invalid_login_rejected_before_api(self):
        self.assertEqual(enroll.read_students(["Alayfolk64"], None), ["Alayfolk64"])
        for login in ("../bad", "student/name", "student@example.org", "student user", "-student"):
            with self.subTest(login=login), self.assertRaises(ValueError):
                enroll.read_students([login], None)

    def test_api_sends_json_over_stdin_and_accepts_empty_success(self):
        result = subprocess.CompletedProcess([], 0, "", "")
        with patch.object(enroll.subprocess, "run", return_value=result) as run:
            self.assertIsNone(enroll.api("PUT", "repos/org/repo/collaborators/student", {"permission": "push"}))
        self.assertEqual(json.loads(run.call_args.kwargs["input"]), {"permission": "push"})
        self.assertEqual(run.call_args.args[0][-2:], ["--input", "-"])

    def test_only_explicit_404_is_treated_as_absent(self):
        for code in (403, 422, 500):
            result = subprocess.CompletedProcess([], 1, "", f"gh: Request failed (HTTP {code})")
            with patch.object(enroll.subprocess, "run", return_value=result), self.assertRaises(RuntimeError):
                enroll.api("GET", "repos/org/repo", missing_ok=True)
        result = subprocess.CompletedProcess([], 1, "", "gh: Not Found (HTTP 404)")
        with patch.object(enroll.subprocess, "run", return_value=result):
            self.assertIsNone(enroll.api("GET", "repos/org/repo", missing_ok=True))


if __name__ == "__main__":
    unittest.main()
