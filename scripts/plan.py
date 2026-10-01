#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成一轮采集任务清单（平台 × 检索词），并跟踪哪些已经采过。

用法:
  python plan.py --out                 # 生成 data/plan-<日期>.md
  python plan.py --list                # 看看还差哪些没采
  python plan.py --done "抖音|coke老师 语录"
  python plan.py --round 2             # 第N轮（轮次只影响清单标题与排序）
"""
import argparse
import json
import os
from collections import OrderedDict
from datetime import datetime
from pathlib import Path

HOME = Path(os.environ.get("COKE_QUOTES_HOME", "")) if os.environ.get(
    "COKE_QUOTES_HOME") else Path.cwd() / "coke-corpus"

SUBJECTS = [
    "coke老师", "coke老师 语录", "Ccoke", "蒋帅", "小猫老弟", "小猫老师",
    "抖一颜", "痞牛", "阿玛特拉斯", "汗流浃背了吧老弟", "我嘞个骚刚",
    "喜欢吗老弟", "我痞吗", "大痞天下", "火影手游 coke",
]
SCENES = [
    "语录", "语录合集", "经典语录", "口头禅", "名场面", "名梗", "台词", "金句",
    "直播切片", "连麦", "PK", "OK了老铁们", "采访", "表情包出处", "梗 出处",
]
PLATFORMS = OrderedDict([
    ("抖音", "浏览器工具人工浏览（脚本抓不到）"),
    ("B站", "浏览器工具 + 视频CC字幕"),
    ("微博", "浏览器工具（搜索页需登录）"),
    ("知乎", "浏览器工具（需登录）"),
    ("贴吧", "fetch_page.py，失败转浏览器"),
    ("梗百科/百科/媒体稿", "fetch_page.py ✅"),
    ("小红书", "浏览器工具（多为二创，严判）"),
])


def log_path():
    return HOME / "crawl-log.jsonl"


def load_log():
    p = log_path()
    if not p.exists():
        return {}
    out = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            r = json.loads(line)
            out[r["key"]] = r
    return out


def tasks():
    for sub in SUBJECTS:
        for sc in SCENES:
            yield f"{sub} {sc}".strip()
    for plat in PLATFORMS:
        yield f"[平台]{plat}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--done")
    ap.add_argument("--round", type=int, default=1)
    args = ap.parse_args()

    HOME.mkdir(parents=True, exist_ok=True)
    log = load_log()

    if args.done:
        with log_path().open("a", encoding="utf-8") as f:
            f.write(json.dumps({"key": args.done,
                                "at": datetime.now().strftime("%Y-%m-%d %H:%M")},
                               ensure_ascii=False) + "\n")
        print(f"已标记采集完成: {args.done}")
        return

    all_tasks = list(tasks())
    todo = [t for t in all_tasks if t not in log]

    if args.list or not args.out:
        print(f"总任务 {len(all_tasks)}，已完成 {len(all_tasks)-len(todo)}，待采 {len(todo)}")
        for t in todo[:60]:
            print("  ☐", t)
        if len(todo) > 60:
            print(f"  ...（还有 {len(todo)-60} 条）")
        return

    today = datetime.now().strftime("%Y%m%d")
    lines = [f"# Coke 语录采集清单 · 第 {args.round} 轮 · {today}", "",
             f"总任务 {len(all_tasks)}，已完成 {len(all_tasks)-len(todo)}，本轮待采 {len(todo)}", "",
             "## 源与采集方式", ""]
    for k, v in PLATFORMS.items():
        lines.append(f"- **{k}**：{v}")
    lines += ["", "## 待采集检索词", ""]
    for t in todo:
        lines.append(f"- [ ] {t}")
    lines += ["", "## 已采过（不再重复）", ""]
    for k, v in log.items():
        lines.append(f"- [x] {k} <sub>{v.get('at','')}</sub>")
    lines += ["", "---", "",
              "采集完把页面正文放进 `raw/`，然后：",
              "```",
              "python harvest.py            # 抽候选句",
              "python corpus.py import data/candidates-<日期>.jsonl   # 复核后入库",
              "python plan.py --done \"<任务>\"   # 标记完成",
              "```", ""]
    out = HOME / f"plan-{today}.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"清单已生成: {out}（待采 {len(todo)} 项）")


if __name__ == "__main__":
    main()
