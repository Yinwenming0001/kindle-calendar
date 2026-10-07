#!/usr/bin/env python3
"""把本仓库一次性推到 GitHub 并点亮 Pages。

用法：
    GITHUB_TOKEN=ghp_xxx python3 upload_to_github.py [--repo kindle-calendar]

需要的 token 权限：repo（全部）、workflow（用于提交 .github/workflows）
"""

import argparse
import base64
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

API = "https://api.github.com"


def req(method, path, token, data=None, allow=()):
    url = API + path
    body = json.dumps(data).encode() if data is not None else None
    r = urllib.request.Request(url, data=body, method=method)
    r.add_header("Authorization", "Bearer " + token)
    r.add_header("Accept", "application/vnd.github+json")
    r.add_header("X-GitHub-Api-Version", "2022-11-28")
    r.add_header("User-Agent", "kindle-calendar-uploader")
    if body:
        r.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            txt = resp.read().decode()
            return resp.status, (json.loads(txt) if txt else {})
    except urllib.error.HTTPError as e:
        txt = e.read().decode()
        if e.code in allow:
            return e.code, (json.loads(txt) if txt else {})
        print(f"\n[error] {method} {path} -> {e.code}\n{txt[:600]}")
        raise SystemExit(1)


def tracked_files(root):
    out = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True)
    return [f for f in out.stdout.split("\n") if f.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="kindle-calendar")
    ap.add_argument("--private", action="store_true")
    a = ap.parse_args()

    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        print("未检测到 GITHUB_TOKEN，请先：export GITHUB_TOKEN=ghp_xxx")
        raise SystemExit(1)

    root = os.path.dirname(os.path.abspath(__file__))
    files = tracked_files(root)
    print(f"待上传 {len(files)} 个文件")

    status, me = req("GET", "/user", token)
    owner = me["login"]
    print(f"GitHub 账号：{owner}")

    status, _ = req("POST", "/user/repos", token, {
        "name": a.repo,
        "description": "Kindle 电子台历（云端渲染 + GitHub Pages 托管）",
        "private": a.private,
        "auto_init": False,
    }, allow=(422,))
    print(f"仓库 {owner}/{a.repo} 就绪")

    _, repo = req("GET", f"/repos/{owner}/{a.repo}", token)

    parents = []
    code, ref = req("GET", f"/repos/{owner}/{a.repo}/git/ref/heads/main", token, allow=(404, 409))
    if code == 200:
        parents = [ref["object"]["sha"]]
        print("仓库已有提交，追加新提交")
    else:
        # 空仓库无法直接建 blob，先用 contents API 造一个初始提交
        print("空仓库，先创建引导提交…")
        import urllib.parse
        seed = base64.b64encode(b"bootstrap\n").decode()
        req("PUT", f"/repos/{owner}/{a.repo}/contents/README.md", token, {
            "message": "bootstrap", "content": seed, "branch": "main",
        })
        _, ref = req("GET", f"/repos/{owner}/{a.repo}/git/ref/heads/main", token)
        parents = [ref["object"]["sha"]]

    entries = []
    for i, f in enumerate(files, 1):
        p = os.path.join(root, f)
        with open(p, "rb") as fh:
            content = base64.b64encode(fh.read()).decode()
        _, blob = req("POST", f"/repos/{owner}/{a.repo}/git/blobs", token,
                      {"content": content, "encoding": "base64"})
        entries.append({"path": f, "mode": "100644", "type": "blob", "sha": blob["sha"]})
        if i % 10 == 0 or i == len(files):
            print(f"  已上传 {i}/{len(files)}", end="\r")

    print("\n生成提交中…")
    _, tree = req("POST", f"/repos/{owner}/{a.repo}/git/trees", token, {"tree": entries})
    _, commit = req("POST", f"/repos/{owner}/{a.repo}/git/commits", token, {
        "message": "Kindle 电子台历：渲染脚本 + 云端定时任务",
        "tree": tree["sha"],
        "parents": parents,
    })

    if parents:
        req("PATCH", f"/repos/{owner}/{a.repo}/git/refs/heads/main", token,
            {"sha": commit["sha"]}, allow=(422,))
    else:
        req("POST", f"/repos/{owner}/{a.repo}/git/refs", token,
            {"ref": "refs/heads/main", "sha": commit["sha"]}, allow=(422,))
        req("PATCH", f"/repos/{owner}/{a.repo}", token, {"default_branch": "main"}, allow=(422,))
    print("推送完成（1 次提交）")

    print("触发首次渲染…")
    req("POST", f"/repos/{owner}/{a.repo}/actions/workflows/calendar.yml/dispatches",
        token, {"ref": "main"}, allow=(204, 404))

    branch_ready = False
    for _ in range(30):
        time.sleep(10)
        code, _ = req("GET", f"/repos/{owner}/{a.repo}/branches/gh-pages", token, allow=(404,))
        if code == 200:
            branch_ready = True
            break
        print("  等待 Actions 生成 gh-pages 分支…", end="\r")
    print("\ngh-pages 分支：" + ("已就绪" if branch_ready else "尚未生成（可稍后再看）"))

    if branch_ready:
        req("POST", f"/repos/{owner}/{a.repo}/pages", token,
            {"source": {"branch": "gh-pages", "path": "/"}}, allow=(409, 204, 201))
        print("Pages 已开启")

    time.sleep(5)
    code, pages = req("GET", f"/repos/{owner}/{a.repo}/pages", token, allow=(404,))
    url = f"https://{owner}.github.io/{a.repo}/calendar.png"
    if code == 200:
        print(f"Pages 状态：{pages.get('status')}  站点：{pages.get('html_url')}")
    print("\n=========================================")
    print(f"台历图片地址（填进 Kindle 配置）：\n{url}")
    print("=========================================")


if __name__ == "__main__":
    main()
