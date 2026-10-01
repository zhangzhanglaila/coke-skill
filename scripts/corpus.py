#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
coke-quotes 语料库管理

用法:
  python corpus.py init
  python corpus.py add --text "汗流浃背了吧，老弟" --scene "击败对手后" \
      --platform 抖音直播 --type 口头禅 --tags 嘲讽,火影 \
      --source-url https://... --confidence 0.9
  python corpus.py import data/candidates-20260101.jsonl
  python corpus.py search 老弟 --limit 20
  python corpus.py stats
  python corpus.py dedupe
  python corpus.py verify q0007
  python corpus.py export --format md  --out 语录合集.md
  python corpus.py export --format html --out 语录卡片.html

数据目录: $COKE_QUOTES_HOME 或 ./coke-corpus
"""
import argparse
import difflib
import json
import os
import re
import sys
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_HOME = Path(os.environ.get("COKE_QUOTES_HOME", "")) if os.environ.get("COKE_QUOTES_HOME") else Path.cwd() / "coke-corpus"
QUOTES_FILE = "quotes.jsonl"
SEEDS = SKILL_DIR / "data" / "seeds.jsonl"

PUNCT = re.compile(r"[\s，。！？、,.!?；;：:\"“”‘’'（）()【】\[\]《》<>—\-…~～*#]")

DISCLAIMER = ("> ⚠ 本合集为个人学习与非商业研究性质的摘录，每条均标注出处。"
              "相关口述内容的著作权归原作者所有；本站/本仓库与当事人及可口可乐公司均无关联。"
              "如为权利人或不希望被收录，请提 issue 或邮件联系，将第一时间删除。")
DISCLAIMER_HTML = ("本页为个人学习与非商业研究性质的摘录，每条均标注出处；"
                   "相关口述内容的著作权归原作者所有。如为权利人请提 issue 联系删除。")


def home() -> Path:
    return DEFAULT_HOME


def norm(text: str) -> str:
    t = unicodedata.normalize("NFKC", text or "")
    t = PUNCT.sub("", t)
    return t.lower()


def load(home_dir: Path):
    p = home_dir / QUOTES_FILE
    if not p.exists():
        return []
    rows = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def save(home_dir: Path, rows):
    p = home_dir / QUOTES_FILE
    with p.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def next_id(rows) -> str:
    mx = 0
    for r in rows:
        m = re.match(r"q(\d+)", str(r.get("id", "")))
        if m:
            mx = max(mx, int(m.group(1)))
    return "q%04d" % (mx + 1)


def find_similar(rows, text, threshold=0.88):
    n = norm(text)
    hits = []
    for r in rows:
        ratio = difflib.SequenceMatcher(None, n, norm(r.get("text", ""))).ratio()
        if ratio >= threshold:
            hits.append((ratio, r))
    hits.sort(key=lambda x: -x[0])
    return hits


# ---------------- 命令 ----------------

def cmd_init(args):
    h = home()
    (h / "raw").mkdir(parents=True, exist_ok=True)
    qf = h / QUOTES_FILE
    if not qf.exists():
        qf.write_text("", encoding="utf-8")
    rows = load(h)
    added = 0
    if SEEDS.exists():
        for line in SEEDS.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            s = json.loads(line)
            if any(norm(s["text"]) == norm(r.get("text", "")) for r in rows):
                continue
            rec = {
                "id": next_id(rows),
                "text": s["text"],
                "type": s.get("type", ""),
                "scene": s.get("scene", ""),
                "platform": s.get("platform", ""),
                "source_url": s.get("source_url", ""),
                "date": s.get("date", ""),
                "tags": s.get("tags", []),
                "confidence": s.get("confidence", 0.6),
                "verified": s.get("verified", False),
                "variant_of": s.get("variant_of"),
                "notes": s.get("notes", ""),
                "added_at": datetime.now().strftime("%Y-%m-%d"),
            }
            rows.append(rec)
            added += 1
        save(h, rows)
    print(f"语料库已就绪: {h}")
    print(f"  现有 {len(rows)} 条（本次导入种子 {added} 条）")
    print(f"  原始页面目录: {h / 'raw'}")


def cmd_add(args):
    h = home()
    rows = load(h)
    text = args.text.strip()
    if not text:
        print("ERROR: --text 不能为空", file=sys.stderr)
        sys.exit(1)
    if not args.source_url:
        print("ERROR: 必须有 --source-url（无出处不入库）", file=sys.stderr)
        sys.exit(1)
    dup = find_similar(rows, text)
    if dup and not args.force:
        top = dup[0]
        print(f"疑似重复（相似度 {top[0]:.2f}）: [{top[1]['id']}] {top[1]['text']}")
        print("  加 --force 强制入库，或改用 verify/variant_of 关联")
        return
    rec = {
        "id": next_id(rows),
        "text": text,
        "type": args.type or "",
        "scene": args.scene or "",
        "platform": args.platform or "",
        "source_url": args.source_url,
        "date": args.date or "",
        "tags": [t for t in (args.tags or "").split(",") if t],
        "confidence": args.confidence,
        "verified": False,
        "variant_of": args.variant_of,
        "notes": args.notes or "",
        "added_at": datetime.now().strftime("%Y-%m-%d"),
    }
    rows.append(rec)
    save(h, rows)
    print(f"已入库 [{rec['id']}] {text}  (共 {len(rows)} 条)")


def cmd_import(args):
    h = home()
    rows = load(h)
    src = Path(args.file)
    raw = src.read_text(encoding="utf-8").strip()
    items = []
    if raw.startswith("["):
        items = json.loads(raw)
    else:
        for line in raw.splitlines():
            line = line.strip()
            if line:
                items.append(json.loads(line))
    added, skipped = 0, 0
    for it in items:
        text = (it.get("text") or "").strip()
        if not text or not it.get("source_url"):
            skipped += 1
            continue
        if find_similar(rows, text) and not args.force:
            skipped += 1
            continue
        rec = {
            "id": next_id(rows),
            "text": text,
            "type": it.get("type", ""),
            "scene": it.get("scene", ""),
            "platform": it.get("platform", ""),
            "source_url": it.get("source_url", ""),
            "date": it.get("date", ""),
            "tags": it.get("tags", []),
            "confidence": float(it.get("confidence", 0.6)),
            "verified": bool(it.get("verified", False)),
            "variant_of": it.get("variant_of"),
            "notes": it.get("notes", ""),
            "added_at": datetime.now().strftime("%Y-%m-%d"),
        }
        rows.append(rec)
        added += 1
    save(h, rows)
    print(f"导入完成: 新增 {added}，跳过 {skipped}（无出处或疑似重复），共 {len(rows)} 条")


def cmd_search(args):
    rows = load(home())
    pat = args.pattern
    out = []
    for r in rows:
        hay = " ".join([r.get("text", ""), r.get("scene", ""), r.get("notes", ""),
                        " ".join(r.get("tags", [])), r.get("platform", ""), r.get("type", "")])
        ok = (re.search(pat, hay, re.I) if args.regex else (pat.lower() in hay.lower()))
        if not ok:
            continue
        if args.tag and args.tag not in r.get("tags", []):
            continue
        if args.type and r.get("type") != args.type:
            continue
        if r.get("confidence", 0) < args.min_confidence:
            continue
        if args.verified_only and not r.get("verified"):
            continue
        out.append(r)
    out.sort(key=lambda r: -r.get("confidence", 0))
    out = out[: args.limit]
    if not out:
        print("没有命中。换个关键词，或先跑一轮采集。")
        return
    for r in out:
        flag = "✔" if r.get("verified") else " "
        print(f"{flag}[{r['id']}] {r['text']}")
        print(f"    场景: {r.get('scene','-')} | {r.get('platform','-')} | {r.get('date','-')} | 置信{r.get('confidence')}")
        if r.get("source_url"):
            print(f"    出处: {r['source_url']}")
        if r.get("notes"):
            print(f"    备注: {r['notes']}")
    print(f"\n共 {len(out)} 条")


def cmd_stats(args):
    rows = load(home())
    if not rows:
        print("语料库为空，先跑 init。")
        return
    print(f"总条数: {len(rows)}")
    print(f"已复核: {sum(1 for r in rows if r.get('verified'))}")
    print(f"平均置信: {sum(r.get('confidence',0) for r in rows)/len(rows):.2f}")
    print("\n按类型:")
    for k, v in Counter(r.get("type", "-") or "-" for r in rows).most_common():
        print(f"  {k:<8} {v}")
    print("\n按平台:")
    for k, v in Counter(r.get("platform", "-") or "-" for r in rows).most_common():
        print(f"  {k:<10} {v}")
    print("\n标签 TOP10:")
    tags = Counter(t for r in rows for t in r.get("tags", []))
    for k, v in tags.most_common(10):
        print(f"  {k:<10} {v}")
    print("\n待核实（置信 < 0.7 或未复核）:")
    for r in rows:
        if r.get("confidence", 0) < 0.7 or not r.get("verified"):
            print(f"  [{r['id']}] {r['confidence']} {'✔' if r.get('verified') else ' '} {r['text']}")


def cmd_dedupe(args):
    rows = load(home())
    seen = set()
    dups = []
    for r in rows:
        n = norm(r.get("text", ""))
        if n in seen:
            dups.append(("完全相同", r, None))
        seen.add(n)
    pairs = []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            ratio = difflib.SequenceMatcher(None, norm(rows[i]["text"]), norm(rows[j]["text"])).ratio()
            if ratio >= args.threshold:
                pairs.append((ratio, rows[i], rows[j]))
    if not dups and not pairs:
        print("没有发现重复。")
        return
    for kind, r, _ in dups:
        print(f"[完全相同] {r['id']} {r['text']}")
    for ratio, a, b in sorted(pairs, key=lambda x: -x[0]):
        print(f"[{ratio:.2f}] {a['id']} 「{a['text']}」  ~  {b['id']} 「{b['text']}」")
    print(f"\n共 {len(dups)+len(pairs)} 组疑似重复（本命令只报告，不自动合并）")


def cmd_verify(args):
    h = home()
    rows = load(h)
    n = 0
    for r in rows:
        if r["id"] in args.ids:
            r["verified"] = args.unverify is False
            if args.confidence is not None:
                r["confidence"] = args.confidence
            n += 1
            print(f"{'✔复核' if r['verified'] else '✗取消复核'} [{r['id']}] {r['text']}")
    save(h, rows)
    print(f"更新 {n} 条")


def cmd_delete(args):
    h = home()
    rows = load(h)
    kept = [r for r in rows if r["id"] not in args.ids]
    save(h, kept)
    print(f"删除 {len(rows)-len(kept)} 条，剩余 {len(kept)} 条")


def cmd_export(args):
    h = home()
    rows = load(h)
    if args.tag:
        rows = [r for r in rows if args.tag in r.get("tags", [])]
    if args.type:
        rows = [r for r in rows if r.get("type") == args.type]
    if args.verified_only:
        rows = [r for r in rows if r.get("verified")]
    rows = [r for r in rows if r.get("confidence", 0) >= args.min_confidence]
    if args.public:
        # 公开发布档：只留已复核 + 高置信，剥掉备注里的个人信息与内部判断
        rows = [r for r in rows if r.get("verified") and r.get("confidence", 0) >= 0.7]
        keep = ("id", "text", "type", "scene", "platform", "date", "tags",
                "source_url", "variant_of", "verified", "confidence")
        rows = [{k: r.get(k) for k in keep} for r in rows]
    rows.sort(key=lambda r: (-r.get("confidence", 0), r.get("id", "")))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    if args.format == "json":
        out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    elif args.format == "md":
        lines = ["# Coke老师语录合集", "",
                 f"> 共 {len(rows)} 条 · 导出于 {datetime.now():%Y-%m-%d} · 每条均附出处", ""]
        if args.public:
            lines += [DISCLAIMER, ""]
        by_type = {}
        for r in rows:
            by_type.setdefault(r.get("type") or "未分类", []).append(r)
        for t, items in by_type.items():
            lines.append(f"## {t}")
            lines.append("")
            for r in items:
                mark = "" if r.get("verified") else "（待核实）"
                lines.append(f"- **{r['text']}**{mark}")
                meta = " / ".join(x for x in [r.get("scene"), r.get("platform"), r.get("date")] if x)
                if meta:
                    lines.append(f"  - {meta}")
                if r.get("source_url"):
                    lines.append(f"  - 出处：{r['source_url']}")
                if r.get("notes"):
                    lines.append(f"  - 备注：{r['notes']}")
            lines.append("")
        out.write_text("\n".join(lines), encoding="utf-8")
    elif args.format == "html":
        body = render_html(rows)
        if args.public:
            body = body.replace("</body>", f"<footer class='disc'>{DISCLAIMER_HTML}</footer></body>")
        out.write_text(body, encoding="utf-8")
    print(f"已导出 {len(rows)} 条 → {out}")


def render_html(rows):
    cards = []
    for r in rows:
        tags = "".join(f"<span class='tag'>#{t}</span>" for t in r.get("tags", []))
        meta = " · ".join(x for x in [r.get("type"), r.get("platform"), r.get("date")] if x)
        src = r.get("source_url", "")
        src_html = f"<a href='{src}' target='_blank'>出处 ↗</a>" if src else "<span class='muted'>出处缺失</span>"
        badge = "" if r.get("verified") else "<span class='badge warn'>待核实</span>"
        scene = r.get("scene", "")
        scene_html = f"<p class='scene'>{scene}</p>" if scene else ""
        cards.append(f"""
    <article class="card">
      <div class="quote">{r['text']}</div>
      {scene_html}
      <div class="meta"><span class="muted">{meta}</span> {badge}</div>
      <div class="foot">{tags} {src_html}</div>
    </article>""")
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>雷霆语言系统 · Coke老师语录卡片</title>
<style>
  :root {{ --bg:#0e0e13; --card:#1c1c28; --ink:#f2f2f5; --muted:#8b8b98;
           --line:rgba(255,255,255,.08); --red:#FE2C55; --cyan:#25F4EE; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; padding:40px 20px 72px; background:var(--bg); color:var(--ink);
         font-family:"PingFang SC","Microsoft YaHei",-apple-system,sans-serif; }}
  .glow {{ position:fixed; border-radius:50%; filter:blur(120px); opacity:.3; pointer-events:none; }}
  .glow.a {{ width:480px; height:480px; background:var(--red); top:-140px; left:-100px; }}
  .glow.b {{ width:420px; height:420px; background:var(--cyan); bottom:-120px; right:-80px; opacity:.18; }}
  header {{ position:relative; max-width:880px; margin:0 auto 30px; }}
  h1 {{ font-size:30px; margin:0 0 8px; letter-spacing:1px; font-weight:800;
        background:linear-gradient(92deg,var(--red) 20%,#fff 50%,var(--cyan) 80%);
        -webkit-background-clip:text; background-clip:text; color:transparent; }}
  .sub {{ color:var(--muted); font-size:13px; }}
  .grid {{ position:relative; max-width:880px; margin:0 auto; display:grid; gap:14px;
           grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); }}
  .card {{ background:linear-gradient(160deg,rgba(254,44,85,.08),rgba(28,28,40,.9) 45%,rgba(37,244,238,.06));
           border:1px solid var(--line); border-radius:16px; padding:20px 20px 14px;
           backdrop-filter:blur(8px); transition:transform .15s,border-color .2s; }}
  .card:hover {{ transform:translateY(-3px); border-color:rgba(254,44,85,.5); }}
  .quote {{ font-size:18px; line-height:1.55; font-weight:700; }}
  .quote::before {{ content:"“"; color:var(--red); margin-right:2px; }}
  .quote::after {{ content:"”"; color:var(--cyan); margin-left:2px; }}
  .scene {{ margin:10px 0 0; font-size:13px; color:#b9b9c6; line-height:1.6; }}
  .meta {{ margin-top:14px; font-size:12px; color:var(--muted);
           display:flex; gap:8px; align-items:center; flex-wrap:wrap; }}
  .foot {{ margin-top:10px; padding-top:10px; border-top:1px dashed var(--line);
           font-size:12px; display:flex; gap:6px; flex-wrap:wrap; align-items:center; }}
  .tag {{ background:rgba(37,244,238,.1); color:var(--cyan); border-radius:6px; padding:2px 7px; }}
  .badge {{ background:rgba(245,181,99,.12); color:#f5b563; border-radius:6px; padding:2px 7px; }}
  a {{ color:var(--cyan); text-decoration:none; }}
  .muted {{ color:var(--muted); }}
</style></head>
<body>
<div class="glow a"></div><div class="glow b"></div>
<header>
  <h1>⚡ 雷霆语言系统 · Coke老师语录卡片</h1>
  <div class="sub">共 {len(rows)} 条 · 生成于 {datetime.now():%Y-%m-%d} · 每条均附出处，转载请保留来源</div>
</header>
<div class="grid">{''.join(cards)}
</div>
</body></html>"""


def main():
    p = argparse.ArgumentParser(description="coke-quotes 语料库管理")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="初始化语料库并导入种子").set_defaults(func=cmd_init)

    a = sub.add_parser("add", help="新增一条语录")
    a.add_argument("--text", required=True)
    a.add_argument("--source-url", required=True)
    a.add_argument("--scene", default="")
    a.add_argument("--platform", default="")
    a.add_argument("--type", default="")
    a.add_argument("--tags", default="")
    a.add_argument("--date", default="")
    a.add_argument("--confidence", type=float, default=0.7)
    a.add_argument("--variant-of", default=None)
    a.add_argument("--notes", default="")
    a.add_argument("--force", action="store_true")
    a.set_defaults(func=cmd_add)

    im = sub.add_parser("import", help="批量导入 jsonl/json")
    im.add_argument("file")
    im.add_argument("--force", action="store_true")
    im.set_defaults(func=cmd_import)

    s = sub.add_parser("search", help="检索")
    s.add_argument("pattern")
    s.add_argument("--regex", action="store_true")
    s.add_argument("--tag")
    s.add_argument("--type")
    s.add_argument("--min-confidence", type=float, default=0.0)
    s.add_argument("--verified-only", action="store_true")
    s.add_argument("--limit", type=int, default=20)
    s.set_defaults(func=cmd_search)

    sub.add_parser("stats", help="统计").set_defaults(func=cmd_stats)

    d = sub.add_parser("dedupe", help="查重报告")
    d.add_argument("--threshold", type=float, default=0.88)
    d.set_defaults(func=cmd_dedupe)

    v = sub.add_parser("verify", help="标记复核通过")
    v.add_argument("ids", nargs="+")
    v.add_argument("--unverify", action="store_true")
    v.add_argument("--confidence", type=float, default=None)
    v.set_defaults(func=cmd_verify)

    de = sub.add_parser("delete", help="删除条目")
    de.add_argument("ids", nargs="+")
    de.set_defaults(func=cmd_delete)

    e = sub.add_parser("export", help="导出")
    e.add_argument("--format", choices=["md", "html", "json"], default="md")
    e.add_argument("--out", default="coke-语录合集.md")
    e.add_argument("--tag")
    e.add_argument("--type")
    e.add_argument("--verified-only", action="store_true")
    e.add_argument("--min-confidence", type=float, default=0.0)
    e.add_argument("--public", action="store_true",
                   help="公开发布档：只导已复核且置信≥0.7，剥离备注并附免责声明")
    e.set_defaults(func=cmd_export)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
