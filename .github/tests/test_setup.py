"""Check setup account isolation, credential handling, and retry behavior."""

from contextlib import redirect_stdout
import importlib.util
from io import StringIO
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("course_setup", Path(__file__).resolve().parents[2] / "setup.py")
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.login = "student"
        self.has_secret = False
        self.branches = sorted(setup.CHAPTERS)
        self.fail_secret = False
        self.needs_login = False
        self.fail_login = False

    def command(self, args, **kwargs):
        args = list(args)
        self.calls.append((args, kwargs.get("input")))
        output = ""
        if args[0] == "git":
            output = "git@github.com:student/2026f-rcore.git"
        elif args[1:3] == ["auth", "status"] and self.needs_login:
            return subprocess.CompletedProcess(args, 1)
        elif args[1:3] == ["auth", "login"] and self.fail_login:
            raise subprocess.CalledProcessError(2, args)
        elif args[1:3] == ["api", "--hostname"]:
            endpoint = args[4]
            if endpoint == "user":
                output = self.login
            elif endpoint.endswith("/branches"):
                output = "\n".join(self.branches)
            else:
                output = json.dumps({"owner": {"login": "student", "type": "User"},
                                     "full_name": "student/2026f-rcore"})
        elif args[1:3] == ["secret", "list"]:
            output = json.dumps([{"name": setup.SECRET_NAME}] if self.has_secret else [])
        elif args[1:3] == ["secret", "set"] and self.fail_secret:
            raise subprocess.CalledProcessError(1, args)
        return subprocess.CompletedProcess(args, 0, stdout=output)

    def execute(self):
        with patch.object(setup.subprocess, "run", side_effect=self.command), \
                patch.object(setup.shutil, "which", return_value="installed"), \
                patch.object(setup.getpass, "getpass", return_value="test-course-token") as prompt, \
                redirect_stdout(StringIO()):
            setup.main()
            return prompt.call_count

    def test_new_fork_sets_secret_via_stdin_and_enables_workflow(self):
        self.assertEqual(self.execute(), 1)
        writes = [(args, value) for args, value in self.calls if args[1:3] == ["secret", "set"]]
        self.assertEqual(len(writes), 1)
        args, value = writes[0]
        self.assertEqual(value, "test-course-token")
        self.assertNotIn(value, args)
        self.assertEqual(args[-1], "github.com/student/2026f-rcore")
        self.assertEqual(self.calls[-1][0][1:3], ["workflow", "enable"])

    def test_existing_secret_is_preserved_without_prompt(self):
        self.has_secret = True
        self.assertEqual(self.execute(), 0)
        self.assertFalse(any(args[1:3] == ["secret", "set"] for args, _ in self.calls))

    def test_first_login_uses_browser_without_uploading_ssh_keys(self):
        self.needs_login = True
        self.execute()
        logins = [args for args, _ in self.calls if args[1:3] == ["auth", "login"]]
        self.assertEqual(len(logins), 1)
        self.assertIn("--web", logins[0])
        self.assertIn("--skip-ssh-key", logins[0])

    def test_cancelled_login_does_not_write(self):
        self.needs_login = True
        self.fail_login = True
        with self.assertRaises(subprocess.CalledProcessError):
            self.execute()
        self.assertFalse(any(args[1] in ("secret", "workflow") for args, _ in self.calls))

    def test_wrong_account_cannot_write(self):
        self.login = "another-account"
        with self.assertRaisesRegex(ValueError, "自己的个人 Fork"):
            self.execute()
        self.assertFalse(any(args[1] in ("secret", "workflow") for args, _ in self.calls))

    def test_missing_chapters_cannot_write(self):
        self.branches = ["main"]
        with self.assertRaisesRegex(ValueError, "缺少章节分支"):
            self.execute()
        self.assertFalse(any(args[1] in ("secret", "workflow") for args, _ in self.calls))

    def test_failed_secret_write_stops_setup(self):
        self.fail_secret = True
        with self.assertRaises(subprocess.CalledProcessError):
            self.execute()
        self.assertFalse(any(args[1] == "workflow" for args, _ in self.calls))

    def test_remote_url_is_not_a_command_or_other_host(self):
        for url in ("git@github.com:student/course.git", "https://github.com/student/course.git",
                    "ssh://git@github.com/student/course.git"):
            self.assertEqual(setup.repository_from_url(url), "student/course")
        for url in ("https://github.com.evil.invalid/student/course", "git@other:student/course",
                    "https://github.com/student/course; command"):
            with self.assertRaises(ValueError):
                setup.repository_from_url(url)


if __name__ == "__main__":
    unittest.main()
