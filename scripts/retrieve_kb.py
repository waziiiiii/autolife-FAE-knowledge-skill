"""Autolife Knowledge Base retrieval script.

Usage:
    python retrieve_kb.py "your question" [--top-k 5] [--url http://...]
"""
import argparse
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_URL = os.environ.get("KB_BASE_URL", "http://100.98.140.155:6185")
USERNAME = os.environ.get("KB_USERNAME", "autolife")
PASSWORD = os.environ.get("KB_PASSWORD", "Autolife@1819")
KB_NAMES = os.environ.get("KB_NAMES", "autolife-docs").split(",")
TOP_K = int(os.environ.get("KB_TOP_K", "5"))


def post_json(url, payload, headers=None):
    h = {"Content-Type": "application/json"}
    if headers:
        h.update(headers)
    data = json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, headers=h, method="POST")
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def retrieve(query, top_k=TOP_K):
    login = post_json(
        f"{BASE_URL}/api/auth/login",
        {"username": USERNAME, "password": PASSWORD},
    )
    token = login["data"]["token"]
    result = post_json(
        f"{BASE_URL}/api/kb/retrieve",
        {"query": query, "kb_names": [n.strip() for n in KB_NAMES], "top_k": top_k},
        {"Authorization": f"Bearer {token}"},
    )
    data = result.get("data", {})
    context = data.get("context_text", "")
    if not context and isinstance(data.get("results"), list):
        parts = []
        for i, item in enumerate(data["results"], 1):
            content = item.get("content", "")
            doc = item.get("doc_name", "unknown")
            score = item.get("score", "")
            if content:
                parts.append(f"[{i}] {doc} (score: {score})\n{content}")
        context = "\n\n---\n\n".join(parts)
    return context


def main():
    parser = argparse.ArgumentParser(description="Query Autolife Knowledge Base")
    parser.add_argument("query", help="Question to search")
    parser.add_argument("--top-k", type=int, default=TOP_K)
    parser.add_argument("--url", default=BASE_URL)
    args = parser.parse_args()
    global BASE_URL
    if args.url:
        BASE_URL = args.url.rstrip("/")
    try:
        result = retrieve(args.query, args.top_k)
        if result:
            print(result)
        else:
            print("Knowledge base returned no relevant content.")
    except (HTTPError, URLError, KeyError, json.JSONDecodeError) as e:
        print(f"Retrieval failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()