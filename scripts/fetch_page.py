#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抓静态页面并存进 data/raw/（纯标准库，无第三方依赖）。

用法:
  python fetch_page.py --url https://gengbaike.cn/doc-view-1143.html
  python fetch_page.py --url-file urls.txt --delay 3

只处理纯 HTML 静态页。遇到登录墙 / 验证码 / 空正文会直接提示改用浏览器工具，
不会尝试绕过 —— 抖音、小红书这类动态页请用浏览器工具人工浏览后另存为 txt。
"""
import argparse
import gzip
import io
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
import os  # noqa: E402
HOME = Path(os.environ.get("COKE_QUOTES_HOME", "")) if os.environ.get(
    "COKE_QUOTES_HOME") else Path.cwd() / "coke-corpus"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

WALL_HINTS = ["登录", "验证", "安全验证", "请先登录", "滑动验证", "access denied"]


def slug(url: str) -> str:
    host = urllib.parse.urlparse(url).netloc.replace(":", "_")
    path = urllib.parse.urlparse(url).path.strip("/").replace("/", "_") or "index"
    path = re.sub(r"[^\w\u4e00-\u9fff.-]", "_", path)[:60]
    return f"{host}__{path}"


def fetch(url: str, timeout: int = 15) -> str:
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Accept-Encoding": "gzip",
    })
    try:
        return _open(req, timeout)
    except urllib.error.URLError as e:
        # 代理/内网环境常见：本地证书链不完整。降级重试并明确提示。
        if "CERTIFICATE_VERIFY_FAILED" in str(e):
            print("  ⚠ 证书校验失败（常见于代理环境），本次降级为不校验证书")
            return _open(req, timeout, insecure=True)
        raise


def _open(req, timeout, insecure=False):
    ctx = None
    if insecure:
        import ssl
        ctx = ssl._create_unverified_context()
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        data = resp.read()
        if resp.headers.get("Content-Encoding") == "gzip":
            data = gzip.GzipFile(fileobj=io.BytesIO(data)).read()
        charset = resp.headers.get_content_charset() or "utf-8"
    return data.decode(charset, errors="ignore")


def visible_len(html: str) -> int:
    body = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.I | re.S)
    body = re.sub(r"<[^>]+>", "", body)
    return len(re.sub(r"\s+", "", body))


def save(url: str, html: str, raw_dir: Path):
    raw_dir.mkdir(parents=True, exist_ok=True)
    p = raw_dir / (slug(url) + ".html")
    p.write_text(html, encoding="utf-8")
    txt = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.I | re.S)
    txt = re.sub(r"<[^>]+>", "\n", txt)
    txt = re.sub(r"&nbsp;?", " ", txt)
    txt = re.sub(r"\n{2,}", "\n", txt).strip()
    (raw_dir / (slug(url) + ".txt")).write_text(txt, encoding="utf-8")
    return p, visible_len(html)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url")
    ap.add_argument("--url-file")
    ap.add_argument("--delay", type=float, default=2.0)
    args = ap.parse_args()

    urls = []
    if args.url:
        urls.append(args.url)
    if args.url_file:
        urls += [l.strip() for l in Path(args.url_file).read_text(
            encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
    if not urls:
        print("需要 --url 或 --url-file", file=sys.stderr)
        sys.exit(1)

    raw_dir = HOME / "raw"
    for i, u in enumerate(urls):
        try:
            html = fetch(u)
        except Exception as e:
            print(f"[失败] {u} → {e}")
            continue
        p, vlen = save(u, html, raw_dir)
        status = "OK"
        if vlen < 300 or any(w in html[:6000] for w in WALL_HINTS):
            status = "疑似登录墙/空正文 → 改用浏览器工具人工浏览"
        print(f"[{status}] {u} → {p.name}（正文 {vlen} 字）")
        if i < len(urls) - 1:
            time.sleep(args.delay)
    print(f"\n存到 {raw_dir}，下一步: python harvest.py")


if __name__ == "__main__":
    main()
