# coke-quotes · Coke老师语录问答 Skill

![Skill](https://img.shields.io/badge/skill-coke--quotes-7F1D1D?style=for-the-badge)
![Version](https://img.shields.io/badge/version-v0.1.0-F97316?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-DC2626?style=for-the-badge)
![Quotes](https://img.shields.io/badge/quotes-39-1D4ED8?style=for-the-badge)

一个可移植的 **Agent Skill**（遵循 [Agent Skills](https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills) 通用规范）：让 AI 基于本地带出处的语料，回答抖音主播 **Coke老师** 的语录、口头禅、名场面与梗的问题。**所有回答只来自语料，不编造语录和出处。**

> 与可口可乐公司（Coca-Cola）无任何关联。

## 特点

- **语料即数据源**：39 条语录，每条附场景、平台、时间、出处链接、置信度与核实状态（截至 2026-09-23：已核实 20 条 / 待核实 19 条）。
- **严谨可溯源**：`verified: false` 的条目标注「待核实」；存在归属争议的（如「我嘞个骚刚啊」有考据称最早出自@鸽子神）会明确说明分歧。
- **零依赖、可移植**：纯 Markdown + JSONL，整个文件夹复制到任意支持 SKILL.md 的 Agent 即可使用。

## 安装

将本仓库克隆/复制为 **`coke-quotes`** 目录（目录名需与 `SKILL.md` 中的 `name` 一致），放入对应 Agent 的 skills 目录：

| 运行环境 | 安装位置 |
|---|---|
| Claude Code（全局） | `~/.claude/skills/coke-quotes/` |
| TRAE（全局，CN 版） | `~/.trae-cn/skills/coke-quotes/` |
| TRAE（项目级） | `<项目>/.trae/skills/coke-quotes/` |
| Codex / 其他兼容 Agent | 其文档约定的 skills 目录 |

```bash
git clone https://github.com/zhangzhanglaila/coke-quotes.git ~/.claude/skills/coke-quotes
```

> 建议 GitHub 仓库名直接使用 **coke-quotes**，使 clone 后的目录名与 skill name 一致，无需额外改名。

## 使用

Agent 会在相关问题出现时自动触发，也可显式要求：

```text
用 coke-quotes 回答：汗流浃背了吧老弟出自哪里？
小猫老弟是什么梗？
coke老师撞车小豪说了什么？
```

典型问法：

- 「xxx 这句语录的出处/场景是什么？」
- 「coke老师有哪些口头禅 / 名场面 / 综艺梗？」
- 「阿玛特拉斯是什么意思？」
- 「哪些语录还没被核实？」

## 文件结构

```text
coke-quotes/
├── SKILL.md                    # Skill 入口：frontmatter + 检索与作答规则
├── README.md                   # 本文件
├── LICENSE                     # MIT
├── agents/
│   └── openai.yaml             # Codex/OpenAI 界面元数据
├── coke-corpus/
│   └── quotes.jsonl            # 权威数据源（每行一条 JSON）
├── Coke老师语录合集.md          # 全量人类可读版（39 条）
├── 公开版-语录合集.md           # 对外分享版（仅媒体强来源，21 条）
├── Coke老师语录卡片.html        # 展示卡片
└── 公开版-语录卡片.html
```

## 语料字段

`coke-corpus/quotes.jsonl` 每行一条：

| 字段 | 含义 |
|---|---|
| `id` | 稳定编号 q0001… |
| `text` | 语录原文 |
| `type` | 口头禅 / 名场面 / 连麦PK / 综艺 / 直播 / 短视频 / 采访 / 称号 |
| `scene` | 使用场景与背景 |
| `platform` | 抖音直播 / 抖音 / 综艺 / 线下活动 / 网络二创 |
| `source_url` | 出处链接 |
| `date` | 大致时间 |
| `tags` | 标签（空耳、痞帅、火影、归属争议 等） |
| `confidence` | 置信度 0–1，< 0.7 为弱证据 |
| `verified` | 是否已核实 |
| `variant_of` | 空耳/变体所源自的原句 |
| `notes` | 备注、争议与待核原因 |
| `added_at` | 入库时间（维护用） |

### 收录原则

1. 每条必须有可点击的出处；无法溯源的网络传言一律不收录。
2. 单一切片/转述来源默认 `verified: false`，待核到原视频后转正。
3. 称号类（如「抖一颜」「痞牛」）与语录分开，不计入「他说过的话」。
4. 欢迎提 issue 补录、纠错或提供原视频链接。

## 免责声明

本仓库为个人学习与非商业研究性质的资料整理。语录口述内容的著作权归原作者及相关平台所有；每条均标注出处，如有侵权或不希望被收录，请提 issue 联系，将第一时间删除。仓库代码与文档（SKILL.md、README、整理脚本、HTML 模板）以 MIT 协议开放。

---

## English

**coke-quotes** is a portable Agent Skill for answering questions about Chinese streamer **Coke老师's** famous quotes, catchphrases, and memes from a local, source-linked corpus (39 entries, 20 verified). Answers never go beyond the corpus. Clone it as `coke-quotes/` into any SKILL.md-compatible agent's skills directory (Claude Code, TRAE, Codex). Code and docs are MIT-licensed; quote content belongs to its original creators and is included for non-commercial research with attribution.
