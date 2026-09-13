"""Configure a student's personal fork for OpenCamp grading."""

import getpass
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

SECRET_NAME = "ARCEOS_2026_SPRING_TOKEN"
CHAPTERS = {"main", "ch1", "ch2", "ch3", "ch4", "ch5", "ch6", "ch7", "ch8"}


def run(*args, capture=False, input_text=None):
    result = subprocess.run(args, check=True, text=True, input=input_text,
                            stdout=subprocess.PIPE if capture else None)
    return result.stdout.strip() if capture else None


def repository_from_url(url):
    match = re.fullmatch(r"(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/)"
                         r"([A-Za-z0-9-]+/[A-Za-z0-9_.-]+?)(?:\.git)?/?", url)
    if not match:
        raise ValueError("origin 必须是 github.com 上个人仓库的 HTTPS 或 SSH 地址。")
    return match[1]


def main():
    root = Path(__file__).resolve().parent
    os.chdir(root)
    (root / "tmp").mkdir(exist_ok=True)
    os.environ["TMPDIR"] = str(root / "tmp")
    for program in ("git", "gh"):
        if not shutil.which(program):
            raise ValueError(f"尚未安装 {program}。GitHub CLI 安装说明：https://cli.github.com/")
    repository = repository_from_url(run("git", "remote", "get-url", "--push", "origin", capture=True))
    # Login and the course token serve different purposes. gh handles browser login.
    auth = subprocess.run(["gh", "auth", "status", "--hostname", "github.com"])
    if auth.returncode:
        print(f"GitHub 登录检查退出状态为 {auth.returncode}，请按提示完成首次登录。", flush=True)
        run("gh", "auth", "login", "--hostname", "github.com", "--web", "--skip-ssh-key")
    login = run("gh", "api", "--hostname", "github.com", "user", "--jq", ".login", capture=True)
    repo = json.loads(run("gh", "api", "--hostname", "github.com", "repos/" + repository, capture=True))
    owner = repo["owner"]["login"]
    if repo["owner"]["type"] != "User" or owner.lower() != login.lower():
        raise ValueError(f"当前登录账号为 {login}，仓库所有者为 {owner}。请在自己的个人 Fork 中运行。")
    repository = repo["full_name"]
    print(f"学员账号：{login}；配置仓库：{repository}；课程：2073。", flush=True)
    branches = run("gh", "api", "--hostname", "github.com", "repos/" + repository + "/branches",
                   "--paginate", "--jq", ".[].name", capture=True).splitlines()
    missing = sorted(CHAPTERS - set(branches))
    if missing:
        raise ValueError("仓库缺少章节分支：" + ", ".join(missing)
                         + "。Fork 时需要取消勾选 Copy the main branch only。")
    target = "github.com/" + repository
    secrets = json.loads(run("gh", "secret", "list", "--repo", target, "--json", "name", capture=True))
    if any(item["name"] == SECRET_NAME for item in secrets):
        print(f"{SECRET_NAME} 已存在，保留原值。", flush=True)
    else:
        token = getpass.getpass("粘贴课程管理员提供的 Token（输入不显示）：").strip()
        if not token:
            raise ValueError("Token 不能为空，未写入任何凭证。")
        # Standard input keeps the credential out of command arguments and source files.
        run("gh", "secret", "set", SECRET_NAME, "--repo", target, input_text=token)
        print("课程 Token 已保存到 GitHub Secret。", flush=True)
    run("gh", "workflow", "enable", "build.yml", "--repo", target)
    print(f"配置完成：{repository} 的 rCore 评分工作流已启用。")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        print(f"配置未完成，退出状态 {error.returncode}：{' '.join(error.cmd)}", file=sys.stderr)
        sys.exit(error.returncode if error.returncode > 0 else 1)
    except (ValueError, EOFError, KeyboardInterrupt) as error:
        sys.exit(str(error) or "配置已取消。")
