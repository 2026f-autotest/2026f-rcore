"""Maintainer-only provisioning: python3 enroll.py LOGIN, or read students.txt."""

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

ORGANIZATION = "2026f-autotest"
TEMPLATE = ORGANIZATION + "/2026f-rcore"
SECRET = "ARCEOS_2026_SPRING_TOKEN"
BRANCHES = {"main", *(f"ch{number}" for number in range(1, 9))}


def api(method, path, data=None, missing_ok=False):
    command = ["gh", "api", "--hostname", "github.com", "--method", method, path]
    if data is not None:
        command += ["--input", "-"]
    result = subprocess.run(command, input=json.dumps(data) if data is not None else None,
                            text=True, capture_output=True)
    if result.returncode:
        if missing_ok and "(HTTP 404)" in result.stderr:
            return None
        raise RuntimeError(f"{method} {path} failed ({result.returncode}):\n"
                           f"{result.stdout}\n{result.stderr}")
    return json.loads(result.stdout) if result.stdout.strip() else None


def read_students(arguments, path):
    if len(arguments) > 1:
        raise ValueError("Usage: python3 enroll.py [GITHUB_LOGIN]")
    lines = arguments if arguments else path.read_text().splitlines()
    students = []
    for line in lines:
        login = line.split("#", 1)[0].strip()
        if not login:
            continue
        if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?", login):
            raise ValueError(f"Invalid GitHub login: {login}")
        if login.lower() not in {name.lower() for name in students}:
            students.append(login)
    if not students:
        raise ValueError("Add GitHub logins to students.txt first.")
    return students


def enroll(student, secret):
    login = student["login"]
    name = "2026f-rcore-" + login
    repository = ORGANIZATION + "/" + name
    endpoint = "repos/" + repository
    repo = api("GET", endpoint, missing_ok=True)
    if repo is None:
        print(f"Creating {repository} with all course branches...", flush=True)
        repo = api("POST", "repos/" + TEMPLATE + "/generate", {
            "owner": ORGANIZATION, "name": name, "private": False,
            "include_all_branches": True,
            "description": f"OpenCamp 2073 rCore coursework for {login}",
        })
    else:
        source = (repo.get("template_repository") or {}).get("full_name", "")
        if source.lower() != TEMPLATE.lower() or repo.get("private"):
            raise ValueError(f"{repository} already exists and is not this public course template; left untouched.")
        print(f"Resuming configuration for {repository}; existing code is preserved.", flush=True)

    # GitHub may finish generating chapter branches after returning the new repo.
    for attempt in range(30):
        branches = api("GET", endpoint + "/branches?per_page=100")
        missing = BRANCHES - {branch["name"] for branch in branches}
        if not missing:
            break
        if attempt == 29:
            raise ValueError(f"{repository} is missing branches: {sorted(missing)}; rerun after generation finishes.")
        time.sleep(2)

    variable_path = endpoint + "/actions/variables/STUDENT_GITHUB"
    variable = api("GET", variable_path, missing_ok=True)
    if variable is None:
        api("POST", endpoint + "/actions/variables", {"name": "STUDENT_GITHUB", "value": login})
    elif variable["value"].lower() != login.lower():
        raise ValueError(f"{repository} is assigned to another student; nothing was overwritten.")

    if secret["visibility"] == "selected":
        api("PUT", f"orgs/{ORGANIZATION}/actions/secrets/{SECRET}/repositories/{repo['id']}")
    api("PUT", endpoint + "/actions/workflows/build.yml/enable")
    invitation = api("PUT", endpoint + "/collaborators/" + login, {"permission": "push"})
    status = "Invitation created; the student must accept it" if invitation else "Repository access is active"
    print(f"{status}: https://github.com/{repository}", flush=True)
    api("POST", endpoint + "/actions/workflows/check-config.yml/dispatches", {"ref": "main"})
    print(f"Configuration check started: https://github.com/{repository}/actions", flush=True)


def main():
    root = Path(__file__).resolve().parent
    os.chdir(root)
    (root / "tmp").mkdir(exist_ok=True)
    os.environ["TMPDIR"] = str(root / "tmp")
    students = read_students(sys.argv[1:], root / "students.txt")
    if not shutil.which("gh"):
        raise ValueError("The maintainer needs GitHub CLI: https://cli.github.com/ . Students do not need it.")
    subprocess.run(["gh", "auth", "status", "--hostname", "github.com"], check=True)
    membership = api("GET", "user/memberships/orgs/" + ORGANIZATION)
    if membership.get("state") != "active" or membership.get("role") != "admin":
        raise ValueError("Run this maintainer script as an owner of " + ORGANIZATION)
    template = api("GET", "repos/" + TEMPLATE)
    if not template.get("is_template") or template.get("private"):
        raise ValueError(TEMPLATE + " must be a public template repository.")
    branches = api("GET", "repos/" + TEMPLATE + "/branches?per_page=100")
    if not BRANCHES.issubset({branch["name"] for branch in branches}):
        raise ValueError("The course template is missing chapter branches.")
    secret = api("GET", f"orgs/{ORGANIZATION}/actions/secrets/{SECRET}")
    if secret.get("visibility") not in ("selected", "all"):
        raise ValueError("Set the organization course secret to Selected repositories or All repositories.")
    # Validate the complete roster before creating any repositories.
    roster = []
    for login in students:
        student = api("GET", "users/" + login)
        if student.get("type") != "User":
            raise ValueError(login + " is not a personal GitHub account.")
        roster.append(student)
    for student in roster:
        enroll(student, secret)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, OSError, subprocess.CalledProcessError) as error:
        sys.exit(str(error))
