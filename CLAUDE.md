# Research Closed-Loop · 学术自动化闭环

NotebookLM + Claude Code + Zotero + ARS + OpenClaw 五引擎学术研究自动化系统。

---

## 快捷命令

### 自然语言（直接对 Claude 说）

#### 全管道
| 触发词 | 做什么 |
|--------|--------|
| **"帮我研究 [课题]"** | 启动完整 6 阶段管道 |
| **"/research [课题]"** | 同上 |

#### 分阶段
| 触发词 | 做什么 | 阶段 |
|--------|--------|------|
| **"搜索文献 [主题]"** | 多源检索 → 去重排序 → 导入 Zotero | 1 |
| **"读论文"** | PDF 提取 → NotebookLM 上传 → 源限定问答 | 2 |
| **"找研究空白"** | 跨文献矛盾检测 → Gap 矩阵 → 可行性排序 | 3 |
| **"规划研究"** | 苏格拉底式对话 → 方法论蓝图 | 4 |
| **"写论文"** | 大纲 → 逐节起草 → 逐句溯源 → 自动引用 | 5 |
| **"修订论文"** | 反馈 → 再验证 → 更新引用 | 6 |

#### 工具
| 触发词 | 做什么 |
|--------|--------|
| **"检查环境"** | 验证 Zotero / NotebookLM / Gemini 三通道 |
| **"重建索引"** | 从 Zotero 重扫全库元数据 |
| **"导出 [LaTeX/DOCX/PDF]"** | 格式转换 |

### Slash 命令

| 命令 | 对应 Skill |
|------|-----------|
| `/research-closed-loop` | 主 workflow skill（全管道） |
| `/lit-search` | 文献检索 |
| `/zotero-lit-index` | Zotero 文献索引 + PDF 提取 |
| `/notebooklm-qa` | NotebookLM 源限定问答 |
| `/gap-finder` | 研究 Gap 分析 |
| `/citation-writer` | 零幻觉写作 + 自动引用 |

### 终端快捷命令

| 命令 | 做什么 |
|------|--------|
| `python scripts/env_setup.py` | 一键环境自检 |
| `nlm login` | NotebookLM 重新认证 |
| `nlm notebook list` | 列出所有 NotebookLM 笔记本 |

---

## 架构

```
用户输入课题
     ↓
Phase 0  准备      → 检查 Zotero → nlm login → Gemini key → 凭据仪表盘
     🛑 所有系统绿灯 / 输入缺失凭据
     ↓
Phase 1  文献发现  → PubMed / arXiv / Semantic Scholar / OpenAlex → Zotero
     🛑 用户选择导入哪些论文
     ↓
Phase 2  深度阅读  → PDF 提取 → NotebookLM MCP (源限定问答，零幻觉)
     🛑 用户选择NotebookLM笔记本 + 审核上传的文献
     ↓
Phase 3  Gap 分析  → synthesis_agent 矛盾检测 → 可行性排序 → 假设生成
     🛑 用户选择要追踪的Gap
     ↓
Phase 4  交互规划  → ars-plan 苏格拉底对话 → 方法论蓝图
     🛑 用户批准研究计划
     ↓
Phase 4.5 数据上传 → (可选) 上传真实数据/图表 → 分析 → 与文献交叉验证
     🛑 确认数据解读 / 跳过（写假设性草稿）
     ↓
Phase 5  写作引用  → 逐节起草 → 逐句溯源 → 自动插 citation → 格式输出
           ↓ (有真实数据)              ↓ (无数据)
       描述实际发现 + 真实图表        假设性/未来式草稿
     🛑 用户逐节审核草稿
     ↓
Phase 6  修订精炼  → 反馈迭代 → Zotero 双向同步
     🛑 用户批准最终版本
```

## 三引擎

| 引擎 | 说明 |
|------|------|
| **NotebookLM** | `nlm` CLI → MCP (主), Gemini Files API (备) |
| **Zotero** | 路径在 `config/zotero_config.json` 中配置 |
| **Claude Code** | 全流程编排 |

## 目录

```
Smart_Brace_Project/
├── CLAUDE.md                    # ← 你在这里
├── config/zotero_config.json    # Zotero路径 + API keys
├── scripts/
│   ├── env_setup.py             # 一键环境自检
│   ├── zotero_connector.py      # Zotero SQLite 读取
│   ├── pdf_extractor.py         # PDF → Markdown 批处理
│   ├── metadata_indexer.py      # 文献元数据 JSON 索引
│   └── notebooklm_bridge.py     # NotebookLM MCP + Gemini 双通道
├── skills/                      # 6 个 workflow skills
├── data/                        # 索引、提取结果、项目状态
├── .claude/                     # Claude Code 配置
└── .claude_skills/              # OpenClaw Medical Skills (869 skills)
```

## 幻觉防护

1. 每条事实性论断 → 可追溯到 Zotero 源文献
2. NotebookLM/Gemini 回答天生源限定
3. 写作时逐句溯源验证，无源的标记 🟡/🔴
4. Zotero 是引用元数据的唯一真相源
