# Research Closed-Loop · 学术自动化闭环

基于 **Google NotebookLM + Claude Code + Zotero + ARS + OpenClaw Medical Skills** 的零幻觉学术研究自动化系统。

> 输入课题方向 → 自动文献检索 → 源限定问答 → Gap分析 → 假设生成 → 交互式规划 → 逐句溯源写作 → Zotero同步

[English](README.md)

---

## 架构

```
用户输入课题
     ↓
Phase 0  准备      → 环境检查 + Skill验证 + 凭据仪表盘
     🛑 所有系统绿灯
     ↓
Phase 1  文献发现  → 多数据库检索 (PubMed/arXiv/Semantic Scholar/OpenAlex + 手动 Embase/WoS/CNKI)
     🛑 用户选择导入哪些论文
     ↓
Phase 2  深度阅读  → PDF提取 → NotebookLM 源限定问答 (零幻觉)
     🛑 选择笔记本 + 审核上传文献
     ↓
Phase 3  Gap分析  → 矛盾检测 → 可行性评分 → 假设生成
     🛑 用户选择研究方向
     ↓
Phase 4  交互规划  → 苏格拉底式对话 → 方法论蓝图
     🛑 用户批准研究方案
     ↓
Phase 4.5 数据上传 → (可选) 真实数据/图表 → 与文献交叉验证
     🛑 确认数据解读
     ↓
Phase 5  写作引用  → 逐节起草 → 逐句溯源 → 自动插入citation → 格式输出
     🛑 逐节审核 → 全稿批准
     ↓
Phase 6  修订精炼  → 反馈迭代 → Zotero双向同步
```

每个阶段都有 🛑 **人工确认门** — 系统必须等你明确选择后才继续。

---

## 快速开始

### 前置要求

- Python 3.12+
- Node.js 20+
- [Zotero](https://www.zotero.org/) (推荐安装 Better BibTeX 插件)
- Google 账号 (可使用 NotebookLM)
- Claude Code (需安装 ARS plugin 和 OpenClaw Medical Skills)

### 安装

```bash
# 1. 克隆项目
git clone https://github.com/YOUR_USERNAME/research-closed-loop.git
cd research-closed-loop

# 2. 安装 Python 依赖
pip install pyzotero PyMuPDF markitdown chromadb google-genai notebooklm-mcp-cli bibtexparser

# 3. 复制并编辑配置文件
cp config/zotero_config.template.json config/zotero_config.json
# 编辑 config/zotero_config.json 填入你的 Zotero 路径、API keys 和 Gemini key

# 4. 认证 NotebookLM
nlm login

# 5. 验证环境
python scripts/env_setup.py
```

### 配置说明

编辑 `config/zotero_config.json`:

| 字段 | 获取方式 |
|------|---------|
| `zotero.api_key` | https://www.zotero.org/settings/keys → "Create New Private Key" |
| `zotero.library_id` | 同一页面 — 你的数字 User ID |
| `zotero.data_dir` | Zotero 数据目录 (包含 `zotero.sqlite` 和 `storage/`) |
| `zotero.install_path` | Zotero 应用程序目录 |
| `notebooklm.gemini_api_key` | https://aistudio.google.com/apikey |
| `notebooklm.gemini_model` | 默认: `gemini-2.5-pro` |

### 开始研究

在 Claude Code 中说：

```
帮我研究 [你的课题]
```

或跳转到特定阶段：

```
帮我搜索关于 [主题] 的文献      → Phase 1
帮我读这些论文                  → Phase 2
找出这个领域的研究空白           → Phase 3
帮我规划研究方法                → Phase 4
帮我写文献综述                  → Phase 5
```

---

## 项目结构

```
research-closed-loop/
├── README.md / README_zh.md
├── CLAUDE.md                        # Claude Code 项目文档
├── .gitignore
├── config/
│   ├── zotero_config.template.json   # 配置模板 (可安全提交)
│   └── zotero_config.json            # 真实配置 (gitignore 排除)
├── scripts/
│   ├── env_setup.py                  # 一键环境自检
│   ├── zotero_connector.py           # Zotero SQLite + pyzotero API 读取
│   ├── pdf_extractor.py              # PDF → Markdown 批处理
│   ├── metadata_indexer.py           # 文献元数据 JSON 索引
│   ├── ref_importer.py               # RIS/BibTeX/CSV/CNKI 解析器
│   ├── notebooklm_bridge.py          # NotebookLM MCP + Gemini 双通道桥接
│   └── state_manager.py             # 项目状态持久化 (跨session恢复)
└── skills/
    ├── research-closed-loop/         # ★ 顶层 workflow skill
    ├── lit-search/                   # 统一文献检索
    ├── zotero-lit-index/             # Zotero 文献索引
    ├── notebooklm-qa/                # 源限定问答
    ├── gap-finder/                   # 研究 Gap 分析
    └── citation-writer/              # 零幻觉写作 + 自动引用
```

---

## 核心特性

### 零幻觉引用协议
- 每条事实性论断必须可追溯到 Zotero 中的源文献
- NotebookLM 回答天生源限定 (只使用上传的文献)
- 写作时逐句验证，无法溯源的标记排除
- Zotero 是引用的唯一真相源

### 人工确认门 (HITL Gates)
- 8 个强制确认节点
- 用户选择论文、笔记本、研究方向、批准方案、逐节审核
- 无自动跳转——你掌控每个决策

### 双写作模式
- **综述模式**: 高质量系统综述/叙述性综述，对标顶刊 (PRISMA 2020)
- **数据驱动模式**: 有真实实验数据的原创论著，按目标期刊定制

### 多数据库导入
- 自动: PubMed, arXiv, bioRxiv, Semantic Scholar, OpenAlex
- 手动: Embase, Web of Science, Scopus, Cochrane, 知网, 万方 (RIS/BibTeX/CSV)

---

## 技能依赖

### ARS Plugin (Academic Research Skills)
`ars-outline` · `ars-lit-review` · `ars-plan` · `ars-citation-check` · `ars-abstract` · `ars-format-convert` · `ars-revision` · `ars-revision-coach`

### OpenClaw Medical Skills (869 个精选技能)
`pubmed-search` · `scientific-writing` · `scientific-manuscript` · `literature-review` · `peer-review` · `hypothesis-generation` · `scientific-problem-selection` · `knowledge-synthesis` · `citation-management` · `pyzotero` · `deep-research` 等 850+ 个

---

## License

MIT
