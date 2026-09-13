"""Upload a document to the Autolife knowledge base via AstrBot API.

Usage:
    python upload_to_kb.py "path/to/document.md" [--kb-name autolife-docs]
    cat summary.md | python upload_to_kb.py - --title "Fix Report: Battery 100%"
"""
import argparse
import json
import os
import sys
import tempfile
import time
from urllib.request import Request, urlopen

from netbird_preflight import ensure_netbird

BASE_URL = os.environ.get("KB_BASE_URL", "http://100.98.140.155:6185")
USERNAME = os.environ.get("KB_USERNAME", "autolife")
PASSWORD = os.environ.get("KB_PASSWORD", "123455")


def post_json(url, payload, headers=None):
    h = {"Content-Type": "application/json"}
    if headers:
        h.update(headers)
    data = json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, headers=h, method="POST")
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def login():
    result = post_json(
        f"{BASE_URL}/api/auth/login",
        {"username": USERNAME, "password": PASSWORD},
    )
    return result["data"]["token"]


def get_kb_id(token, kb_name):
    req = Request(
        f"{BASE_URL}/api/kb/list",
        headers={"Authorization": f"Bearer {token}"},
    )
    with urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    items = data.get("data", {})
    if isinstance(items, dict):
        items = items.get("items", []) or items.get("list", [])
    for kb in items:
        if (kb.get("kb_name") or kb.get("name")) == kb_name:
            return kb.get("kb_id") or kb.get("id")
    return None


def upload_file(token, kb_id, file_path, title=None):
    filename = title or os.path.basename(file_path)
    boundary = "----AstrBotUploadBoundary"
    with open(file_path, "rb") as f:
        file_data = f.read()

    body = b""
    body += (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="kb_id"\r\n\r\n'
        f"{kb_id}\r\n"
    ).encode("utf-8")
    body += (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="files"; filename="{filename}"\r\n'
        f"Content-Type: text/markdown\r\n\r\n"
    ).encode("utf-8")
    body += file_data
    body += f"\r\n--{boundary}--\r\n".encode("utf-8")

    content_type = f"multipart/form-data; boundary={boundary}"
    req = Request(
        f"{BASE_URL}/api/kb/document/upload",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": content_type,
        },
        method="POST",
    )
    with urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_json(url, token):
    req = Request(url, headers={"Authorization": f"Bearer {token}"})
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def wait_for_upload(token, task_id, timeout_seconds=900):
    deadline = time.time() + timeout_seconds
    last = {}
    while time.time() < deadline:
        last = get_json(
            f"{BASE_URL}/api/kb/document/upload/progress?task_id={task_id}",
            token,
        )
        payload = last.get("data", {})
        status = payload.get("status")
        if status == "completed":
            result = payload.get("result", {})
            if result.get("failed_count"):
                raise RuntimeError(f"部分文件处理失败：{result.get('failed')}")
            return result
        if status == "failed":
            raise RuntimeError(payload.get("error") or "知识库处理失败")
        time.sleep(2)
    raise TimeoutError(f"上传任务 {task_id} 等待超时")


def main():
    try:
        ensure_netbird()
    except (OSError, RuntimeError) as exc:
        print(f"NetBird 预检失败：{exc}", file=sys.stderr)
        return 2

    parser = argparse.ArgumentParser(description="Upload document to Autolife KB")
    parser.add_argument("file", help="Path to the file to upload, or - for stdin")
    parser.add_argument("--kb-name", default=os.environ.get("KB_NAMES", "autolife-docs"))
    parser.add_argument("--title", default=None, help="Document title (defaults to filename)")
    args = parser.parse_args()

    if not USERNAME or not PASSWORD:
        print("请设置 KB_USERNAME 和 KB_PASSWORD", file=sys.stderr)
        return 2

    if args.file == "-":
        content = sys.stdin.read()
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8")
        tmp.write(content)
        tmp.close()
        file_path = tmp.name
        if not args.title:
            args.title = "Untitled KB Entry.md"
    else:
        file_path = args.file
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}", file=sys.stderr)
            sys.exit(1)

    token = login()
    kb_id = get_kb_id(token, args.kb_name)
    if not kb_id:
        print(f"Knowledge base '{args.kb_name}' not found.", file=sys.stderr)
        sys.exit(1)

    result = upload_file(token, kb_id, file_path, args.title)
    task_id = (result.get("data") or {}).get("task_id")
    if not task_id:
        print(f"上传接口未返回 task_id：{result}", file=sys.stderr)
        sys.exit(1)

    processed = wait_for_upload(token, task_id)
    print(f"Uploaded: {args.title or os.path.basename(file_path)}")
    print(f"Processed: {processed}")

    if args.file == "-":
        os.unlink(file_path)


if __name__ == "__main__":
    main()
