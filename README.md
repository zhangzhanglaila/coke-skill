# 🐱 coke-skill · Coke老师语录问答 Skill

| 简体中文 | English |
|---|---|
| coke-skill 是一个语录考据技能：让 AI 像弹幕里最懂梗的那位老粉一样，回答 Coke老师 的口头禅、名场面与梗——每一句都带出处、场景和核实状态，查不到就承认，绝不编梗。 | coke-skill is a quote-research skill: your AI answers questions about Chinese streamer Coke老师's catchphrases and memes like the most knowledgeable fan in the chat — every line comes with a source, scene, and verification status; never fabricated. |

![Skill](https://img.shields.io/badge/skill-coke--skill-7F1D1D?style=for-the-badge)
![Version](https://img.shields.io/badge/version-v0.1.0-F97316?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-DC2626?style=for-the-badge)
![Quotes](https://img.shields.io/badge/quotes-40%20%7C%2020%20verified-1D4ED8?style=for-the-badge)

**Language / 语言:** [简体中文](#简体中文) | [English](#english)

---

## 简体中文

### 它是什么

> 网络会记住每一句爆火的梗，而这个 skill 记得它们第一次响起的地方。

coke-skill 是一个遵循 [Agent Skills](https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills) 通用规范的可移植技能，内置一份逐条考据的 Coke老师（火影手游顶流主播）语录语料。你问梗，它不只给你原句，还给你**当时的场景、时间、平台和可点击的出处链接**；没有把握的句子会大大方方标「待核实」，而不是一本正经地胡说八道。

| 核心亮点 | 表现 |
|---|---|
| 🔗 句句有出处 | 40 条语录全部附来源链接，媒体稿、百科词条、原视频切片分类可查 |
| ✅ 核实分级 | 已核实 20 条 / 待核实 20 条，置信度 0–1 打分，弱证据主动提示 |
| ⚖️ 争议不回避 | 「我嘞个骚刚啊」归属存在@鸽子神之争，会把双方证据都摆出来 |
| 🐱 梗脉讲得清 | 「小猫老弟」←「喜欢吗，老弟」，空耳、变体、称号之间的关系一目了然 |
| 📦 零依赖开箱 | 纯 Markdown + JSONL，Claude Code / TRAE / Codex 复制即用 |

### 适用场景

- 想知道某句梗的**出处、时间和名场面背景**（汗流浃背了吧老弟、阿玛特拉斯、小豪杀手……）。
- 想按类型浏览：口头禅 / 名场面 / 连麦PK / 综艺 / 直播 / 采访 / 称号。
- 想区分**原创句、空耳变体和粉丝称号**，写文章、做二创、做科普时不张冠李戴。
- 想查哪些语录「大家都在传但其实还没被证实」，避免以讹传讹。
- 需要把语料二次加工：导出合集、做卡片、做可视化（jsonl 是唯一数据源）。

### 不适用场景

- 语料未收录的语录不会用网络脑补——它会直接说「未收录」并给相近候选。
- 不提供直播回放、原视频下载或任何平台内的实时数据。
- 与可口可乐公司（Coca-Cola）无任何关联，也不回答品牌相关问题。

### 快速使用

将本仓库克隆为 **`coke-skill`** 目录（目录名需与 `SKILL.md` 中的 `name` 一致），放入对应 Agent 的 skills 目录：

| 运行环境 | 安装位置 |
|---|---|
| Claude Code（全局） | `~/.claude/skills/coke-skill/` |
| TRAE（全局，CN 版） | `~/.trae-cn/skills/coke-skill/` |
| TRAE（项目级） | `<项目>/.trae/skills/coke-skill/` |
| Codex / 其他兼容 Agent | 其文档约定的 skills 目录 |

```bash
git clone https://github.com/zhangzhanglaila/coke-skill.git ~/.claude/skills/coke-skill
```

相关问题出现时会自动触发，也可以显式调用：

```text
用 coke-skill 回答：汗流浃背了吧老弟出自哪里？
```

常见触发句：

```text
小猫老弟是什么梗？跟「喜欢吗老弟」什么关系？
coke老师撞车职业选手小豪的时候说了什么？
阿玛特拉斯是日语空耳吗？哪年火的？
他在《OK了老铁们》里有哪些名场面？
哪些语录目前还是待核实状态？
```

### 效果演示

**问：**「汗流浃背了吧，老弟」出自哪？

```text
✅ 已核实 · 置信度 0.95

「汗流浃背了吧，老弟」—— 对局击败对手后嘲讽对方疲于应付。
平台/时间：抖音直播 / 2023-10
出处：百度百科词条已收录（附完整链接）
后续：从游戏圈调侃演变成全网表达「尴尬/无奈」的抽象符号。
```

**问：**「我嘞个骚刚啊」是他说的吗？

```text
⚠️ 待核实 · 归属争议（置信度 0.65）

游戏矩阵、克劳锐等媒体将其列为 coke 代表作；
但有梗百科考据称语音最早出自火影圈主播 @鸽子神，
因两人声线相似被误传，二创中普遍使用 coke 形象。
结论：能讲的只有分歧本身，需核到原视频才能定论。
```

**问：**「小猫老弟」是他发明的词吗？

```text
🐱 它是空耳变体，不是独立原创句。
源自他早期口头禅「喜欢吗，老弟」——语速太快被听成「小猫」，
加上十级美颜照片，最终从空耳变成外号（q0002 → q0003）。
```

### 文件结构

```text
coke-skill/
├── SKILL.md                    # 技能入口：触发说明 + 检索与作答规则
├── README.md                   # 本文件
├── LICENSE                     # MIT
├── agents/
│   └── openai.yaml             # Codex/OpenAI 界面元数据
├── coke-corpus/
│   └── quotes.jsonl            # 权威数据源（每行一条 JSON，共 40 条）
├── Coke老师语录合集.md          # 全量人类可读版（40 条）
├── 公开版-语录合集.md           # 对外分享版（仅媒体强来源，21 条）
├── Coke老师语录卡片.html        # 展示卡片
└── 公开版-语录卡片.html
```

### 关键文件

| 文件 | 用途 |
|---|---|
| [`SKILL.md`](SKILL.md) | 技能入口：frontmatter 触发词、检索流程、核实状态与争议的表达规则 |
| [`coke-corpus/quotes.jsonl`](coke-corpus/quotes.jsonl) | 唯一权威数据源，字段说明见下表 |
| [`agents/openai.yaml`](agents/openai.yaml) | Codex/OpenAI 的展示名、短描述与默认提示词 |
| 两个 `.md` 合集 | 按分类组织的人类可读版，公开版只收录媒体强来源 |
| 两个 `.html` 卡片 | 语录展示页，仅供浏览，不作为信息来源 |

### 语料字段与收录原则

`quotes.jsonl` 每行一条，字段：`id` · `text` · `type` · `scene` · `platform` · `source_url` · `date` · `tags` · `confidence`（0–1，<0.7 为弱证据）· `verified` · `variant_of`（空耳/变体源头）· `notes` · `added_at`。

- 每条**必须有可点击出处**；无源传言一律不收录。
- 单一切片/转述默认「待核实」，核到原视频后转正。
- 称号类（抖一颜、痞牛、保底机制）与语录**分库标注**，不计入「他说过的话」。
- 欢迎提 issue 补录、纠错或甩来原视频链接。

### 设计原则

- 宁可说「语料没有」，也不造一句听起来很像的假语录。
- 争议本身就是答案的一部分——证据摆全，让读者自己判断。
- 梗的乐趣在语境：原句之外，永远交代场景、平台和时间。
- 数据对机器友好（JSONL），阅读对人类友好（Markdown 合集）。

### 免责声明

本仓库为个人学习与非商业研究性质的资料整理。语录口述内容的著作权归原作者及相关平台所有，每条均标注出处；如有侵权或不希望被收录，请提 issue 联系，将第一时间删除。代码与文档（SKILL.md、README、HTML 模板等）以 MIT 协议开放。

---

## English

### What It Is

> The internet remembers every meme that went viral. This skill remembers where each one was first spoken.

**coke-skill** is a portable [Agent Skills](https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills)-compatible skill with a hand-verified corpus of quotes from **Coke老师**, a top *Naruto* mobile-game streamer on Douyin. Ask about a meme and you get not just the line, but the **scene, date, platform, and a clickable source** — with uncertain entries openly marked "pending verification" instead of confident-sounding guesses.

| Highlight | What You Get |
|---|---|
| 🔗 Every line sourced | All 40 entries carry source links: media articles, wiki entries, or original video clips |
| ✅ Verification tiers | 20 verified / 20 pending, each scored 0–1 with weak evidence flagged |
| ⚖️ Disputes surfaced | The "我嘞个骚刚啊" attribution dispute (@鸽子神 vs coke) is presented with evidence from both sides |
| 🐱 Meme lineage mapped | "小猫老弟" ← "喜欢吗，老弟": homophones, variants, and nicknames kept distinct |
| 📦 Zero dependencies | Plain Markdown + JSONL; drop into Claude Code, TRAE, or Codex and go |

### When To Use

- Finding the **source, date, and story** behind a catchphrase or legendary moment.
- Browsing by type: catchphrases, iconic moments, PK streams, variety shows, interviews, nicknames.
- Separating **original lines, homophone variants, and fan-made titles** for articles or explainers.
- Checking which quotes are widely circulated but not yet verified.
- Repurposing the data: collections, cards, visualizations (JSONL is the single source of truth).

### When Not To Use

- Quotes outside the corpus are never improvised — the skill says "not collected" and suggests close matches.
- No live-stream replay, video downloads, or real-time platform data.
- Unrelated to The Coca-Cola Company.

### Quick Start

Clone as **`coke-skill`** (folder name must match the `name` in `SKILL.md`) into your agent's skills directory:

```bash
git clone https://github.com/zhangzhanglaila/coke-skill.git ~/.claude/skills/coke-skill
```

Paths: Claude Code → `~/.claude/skills/` · TRAE CN global → `~/.trae-cn/skills/` · TRAE project → `<project>/.trae/skills/` · Codex → its documented skills folder.

```text
Use coke-skill: where does "汗流浃背了吧，老弟" come from?
What meme is "小猫老弟", and how does it relate to "喜欢吗，老弟"?
What did coke say when he matched against pro player 小豪?
```

### Example Answers

```text
✅ Verified (0.95) — "汗流浃背了吧，老弟": post-win trash talk in a duel,
Douyin Live, 2023-10, source: Baidu Baike entry. Later became a universal
expression of awkwardness/helplessness across the Chinese internet.

⚠️ Pending (0.65) — "我嘞个骚刚啊": media list it as coke's, but a meme-wiki
investigation traces the voice to fellow streamer @鸽子神; their voices sound
alike. Both sides are reported; an original video is needed to settle it.

🐱 "小猫老弟" is not an original phrase — it is a fast-speech homophone of his
early catchphrase "喜欢吗，老弟", later reinforced by his heavily-filtered
selfies, and eventually became his nickname.
```

### Design Principles

- "Not in the corpus" beats a plausible-sounding fabrication, every time.
- A dispute is part of the answer — present all evidence, let the reader decide.
- A meme lives in its context: always include scene, platform, and date.
- Machine-friendly data (JSONL), human-friendly reading (Markdown collections).

### Disclaimer

A personal, non-commercial research archive. Spoken content belongs to its creators and platforms; every entry is attributed and can be removed on request via an issue. Skill code and documentation are released under the MIT License. Not affiliated with The Coca-Cola Company.

---

## GitHub Repository Metadata

| Item | Value |
|---|---|
| Repository | [`zhangzhanglaila/coke-skill`](https://github.com/zhangzhanglaila/coke-skill) |
| Skill name | `coke-skill` |
| Display name | Coke Skill / Coke老师语录问答 |
| Version | `0.1.0` |
| Language / 语言 | [简体中文](#简体中文) / [English](#english) |
| License | MIT（代码与文档；语料内容归原权利人所有） |
| Corpus | 40 entries · 20 verified / 20 pending · last updated 2026-09-23 |
| Primary files | `SKILL.md`, `agents/openai.yaml`, `coke-corpus/quotes.jsonl` |

### Topics

`agent-skill` · `claude-skill` · `trae-skill` · `codex-skill` · `chinese-memes` · `douyin` · `naruto-mobile` · `coke` · `corpus` · `jsonl` · `bilingual`

### Stats

![GitHub stars](https://img.shields.io/github/stars/zhangzhanglaila/coke-skill?style=social)
![GitHub forks](https://img.shields.io/github/forks/zhangzhanglaila/coke-skill?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/zhangzhanglaila/coke-skill)

### Notes

- This repository is a Skill package, not an npm package.
- The README is user-facing; agent behavior and answering rules live in `SKILL.md`.
- Quote content is collected for non-commercial research with attribution; the MIT License covers code and documentation only.
