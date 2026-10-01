#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 data/raw/ 抓取到的页面里抽取「可能是 coke 本人说的话」的候选句。

用法:
  python harvest.py                      # 扫描 raw/ 全部文件
  python harvest.py --min-score 5        # 只输出高分候选
  python harvest.py --file raw/xxx.html  # 只处理一个文件

输出: data/candidates-<日期>.jsonl（带 score，需人工复核后才可 import 进语料库）
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))
from corpus import home, norm, load  # noqa: E402

LEXICON = [w.strip() for w in (SKILL_DIR / "references" / "lexicon.txt").read_text(
    encoding="utf-8").splitlines() if w.strip()]

TAG_RE = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.I | re.S)
HTML_RE = re.compile(r"<[^>]+>")
SENT_SPLIT = re.compile(r"(?<=[。！？!?…\n])")

QUOTE_PAIRS = [("“", "”"), ("\"", "\""), ("「", "」"), ("‘", "’")]

NOISE = ["网友说", "据说", "小编", "记者", "本文", "版权", "侵权请联系", "关注", "表示，", "纷纷", "转载", "免责"]
LEADS = ["他说", "一句", "来了句", "脱口而出", "蹦出", "接了一句", "抛出", "张嘴就", "喊出", "问了一", "补了一句", "插了一句"]


def html_to_text(raw: str) -> str:
    raw = TAG_RE.sub("", raw)
    raw = HTML_RE.sub("\n", raw)
    raw = re.sub(r"&nbsp;?", " ", raw)
    raw = re.sub(r"&[a-zA-Z#0-9]+;", "", raw)
    raw = re.sub(r"[ \t]+", " ", raw)
    raw = re.sub(r"\n{2,}", "\n", raw)
    return raw.strip()


def split_sentences(text: str):
    out = []
    for chunk in SENT_SPLIT.split(text):
        c = chunk.strip()
        if c:
            out.append(c)
    return out


def unquote(s: str):
    for l, r in QUOTE_PAIRS:
        if s.startswith(l) and s.endswith(r) and len(s) > 2:
            return s[1:-1].strip(), True
    return s, False


QUOTED_RE = re.compile(r"[“\"「『]([^“”\"」』]{2,80})[”\"」』]")


def score(sentence: str, quoted: bool = None, context: str = "") -> int:
    s, q = unquote(sentence)
    if quoted is None:
        quoted = q
    n = len(s)
    sc = 0
    if quoted and 2 <= n <= 60:
        sc += 3
    if any(w in s for w in LEXICON):
        sc += 3
    if any(w in s for w in ["老弟", "痞", "我嘞个", "咪咪", "阿玛特拉斯"]):
        sc += 2
    if 4 <= n <= 30:
        sc += 1
    if any(w in context for w in LEADS):
        sc += 2
    if any(w in s for w in NOISE):
        sc -= 2
    if any(w in context for w in ["网友", "粉丝说", "弹幕"]):
        sc -= 1
    if n > 80:
        sc -= 2
    if not quoted and s.endswith(("的", "了", "和", "与")):
        sc -= 1
    return sc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file")
    ap.add_argument("--min-score", type=int, default=5)
    ap.add_argument("--limit", type=int, default=200)
    args = ap.parse_args()

    h = home()
    raw_dir = h / "raw"
    if not raw_dir.exists():
        print(f"没有 {raw_dir}，先用 fetch_page.py 或浏览器工具存些页面进来。", file=sys.stderr)
        sys.exit(1)

    files = [Path(args.file)] if args.file else sorted(
        p for p in raw_dir.iterdir() if p.suffix.lower() in {".txt", ".html", ".htm", ".md"})
    if not files:
        print("raw/ 是空的。")
        return

    rows = load(h)
    existing = {norm(r.get("text", "")) for r in rows}
    known_texts = [r.get("text", "") for r in rows]

    candidates, seen = [], set()

    def push(s, sc, source):
        s = s.strip()
        if not (2 <= len(s) <= 120):
            return
        if sc < args.min_score:
            return
        n = norm(s)
        if not n or n in seen or n in existing:
            return
        if any(n and (n in norm(k) or norm(k) in n) for k in known_texts if k):
            return
        seen.add(n)
        candidates.append({
            "text": s, "score": sc, "source_file": source, "source_url": "",
            "platform": "", "scene": "", "type": "", "confidence": 0.6,
            "verified": False, "notes": "harvest 自动抽取，待人工复核",
        })

    for fp in files:
        raw = fp.read_text(encoding="utf-8", errors="ignore")
        text = html_to_text(raw) if fp.suffix.lower() in {".html", ".htm"} else raw
        for para in re.split(r"[\n]+", text):
            # 1) 引号内的句子：原话概率最高
            for m in QUOTED_RE.finditer(para):
                ctx = para[max(0, m.start() - 25):m.start()]
                push(m.group(1), score(m.group(1), quoted=True, context=ctx), fp.name)
            # 2) 无引号的句子：必须命中词库才留（否则全是导航/标题噪音）
            for sent in split_sentences(para):
                if QUOTED_RE.search(sent):
                    continue
                s = sent.strip()
                hit = any(w in s for w in LEXICON) or any(
                    w in s for w in ["老弟", "痞", "我嘞个", "咪咪", "阿玛特拉斯"])
                if not hit:
                    continue
                push(s, score(s, quoted=False), fp.name)

    candidates.sort(key=lambda c: -c["score"])
    candidates = candidates[: args.limit]
    out = h / f"candidates-{datetime.now():%Y%m%d}.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for c in candidates:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"候选 {len(candidates)} 条 → {out}")
    print("下一步：人工复核 → 补全 source_url → python corpus.py import " + str(out))
    for c in candidates[:15]:
        print(f"  [{c['score']}] {c['text']}")


if __name__ == "__main__":
    main()
