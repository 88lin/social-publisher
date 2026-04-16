<div align="center">

![AmpliPost Banner](./banner.svg)

<br>

[![License](https://img.shields.io/badge/License-MIT-6366f1?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-06b6d4?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Multi--Agent-8b5cf6?style=flat-square)](https://docs.anthropic.com/claude-code)
[![Playwright](https://img.shields.io/badge/Playwright-Latest-10b981?style=flat-square&logo=playwright&logoColor=white)](https://playwright.dev)
[![Scrapling](https://img.shields.io/badge/Scrapling-0.4.3+-f59e0b?style=flat-square)](https://github.com/D4Vinci/Scrapling)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-f43f5e?style=flat-square)](CONTRIBUTING.md)

<br>

**AmpliPost** 是基于 **Claude Code Multi-Agent 架构**构建的智能营销中台。三个协作 Agent（content-coordinator、content-reviewer、publish-guard）分工明确，配合 Hooks 系统与长期记忆，将「一句话指令」转化为跨平台内容的全自动生产与分发——无需人工确认，无需手动操作，全程自主决策。

<br>

[快速开始](#-快速开始) · [Multi-Agent 架构](#-multi-agent-架构) · [发布流水线](#-发布流水线) · [平台矩阵](#-平台矩阵) · [Hooks 系统](#-hooks-系统) · [长期记忆](#-长期记忆)

</div>

---

## 为什么是 Multi-Agent

传统自动化脚本的瓶颈不在执行，而在判断。内容质量好不好？这次发布会不会触发风控？这两个问题如果由同一个 Agent 自问自答，天然存在偏差——生成方对自己的内容打分会偏高，风控判断也缺乏独立的历史数据视角。

AmpliPost 的解法是**职责分离**：content-coordinator 只负责生成和调度，content-reviewer 独立评审内容质量（宁可打低，不打高），publish-guard 专注行为维度的风控评估（频率、间隔规律性、内容多样性）。三者通过结构化 JSON 通信，互不干涉，形成真正的制衡机制。

---

## 🤖 Multi-Agent 架构

![Architecture](./architecture.svg)

### 三 Agent 职责边界

<table>
<tr>
<th width="20%">Agent</th>
<th width="40%">职责</th>
<th width="40%">不做什么</th>
</tr>
<tr>
<td><strong>content-coordinator</strong><br><sub>主 Agent</sub></td>
<td>解析用户输入、生成各平台内容、调度 subagent、执行发布、汇报结果、更新记忆</td>
<td>不自评内容质量、不做风控判断</td>
</tr>
<tr>
<td><strong>content-reviewer</strong><br><sub>质量评审</sub></td>
<td>从钩子强度、信息密度、真实感、平台适配、多样性五个维度独立评分，给出具体修改建议</td>
<td>不生成内容、不做发布决策</td>
</tr>
<tr>
<td><strong>publish-guard</strong><br><sub>风控守卫</sub></td>
<td>评估发布频率、间隔规律性、内容多样性、账号行为特征，输出 allow / delay / block 三态决策</td>
<td>不评价内容质量、不修改内容</td>
</tr>
</table>

### 自主决策边界

Agent 在以下情况**自主处理，不询问用户**：未指定平台时根据内容类型推断目标平台；抖音无图时自动调用 `generate_images.py` 生成信息图；内容含违禁词时自动替换；内容质量不达标时交 reviewer 评审并按建议重写（最多 2 次）；风控评估为 delay 时等待随机延迟后发布；发布失败可修复时自动重试（最多 3 次）。

**只有两种情况会停下来询问用户**：登录态失效（需手动扫码，物理限制）；指令完全歧义（主题空白，无法推断）。

---

## 🚀 快速开始

### 安装依赖

```bash
# Playwright 浏览器自动化
npm install -g agent-browser
agent-browser install

# Scrapling 反爬增强
pip install "scrapling[all]>=0.4.3"
scrapling install --force
```

### 配置 API Key

```bash
cp keys.example.txt keys.txt
# 编辑 keys.txt，填入各平台所需的 API Key
```

### 一句话触发全链路

```bash
# 内容类型自动推断平台（干货 → 小红书 + 抖音 + B站）
"帮我发：2025年最值得入手的5款AI工具"

# 指定平台
"发小红书和抖音：职场效率提升的3个反直觉技巧"

# 闲鱼商品（自动识别为商品类 → 闲鱼 + 小红书）
"帮我发闲鱼：iPhone 15 Pro Max 256G，5999元，95新"

# 深度技术文章（→ B站 + 小红书）
"写一篇关于 Scrapling 反爬原理的深度文章"
```

### 首次登录

```bash
# 各平台首次使用需手动扫码（90秒窗口期），之后 Cookie 自动复用
# 登录态存储路径：
# 闲鱼: ~/.openclaw/browser_profiles/xianyu_default/
# 小红书: ~/.catpaw/xhs_browser_profile/
# B站:   ~/.catpaw/bilibili_browser_profile/
# 抖音:  ~/.catpaw/douyin_browser_profile/
```

---

## 🔄 发布流水线

![Pipeline](./scrapling-flow.svg)

完整流水线共 8 个阶段，全程自动执行：

**Phase 0** 读取 `memory.md`，提取历史有效内容方向、用户偏好、内容指纹和风控日志，为后续生成提供参考。

**Phase 1–2** 解析用户输入，推断目标平台，查找各平台 Skill 脚本路径，处理图片决策树（抖音无图自动生成，小红书无图使用文字配图模式）。

**Phase 3** 为每个目标平台独立生成内容，严格遵循各平台字数、结构、风格规格，禁止平台间内容互相复制。

**Phase 3.5** 调用 content-reviewer subagent 进行独立质量评审，总分低于 70 分则按具体建议重写，最多重写 2 次。

**Phase 4.5** 调用 publish-guard subagent 进行风控评估，delay 决策时等待随机延迟，block 决策时跳过并在报告中说明原因。

**Phase 5–8** 依次调用各平台 Skill 脚本执行发布（平台间间隔 15 秒），验证成功标志，输出表格报告，将本次发布记录和内容指纹写入 `memory.md`。

---

## 🎯 平台矩阵

<table>
<tr>
<th align="center" width="25%">🐟 闲鱼</th>
<th align="center" width="25%">📕 小红书</th>
<th align="center" width="25%">📺 B站专栏</th>
<th align="center" width="25%">🎵 抖音图文</th>
</tr>
<tr>
<td>

标题 10–30 字<br>
【新旧程度】商品名 规格<br>
违禁词自动替换<br>
AI 配图可选<br>
登录态持久化

</td>
<td>

标题 ≤20 字<br>
正文 200–300 字<br>
四段结构：痛点→干货→收尾→互动<br>
无图使用文字配图模式<br>
Scrapling 增强 ✅

</td>
<td>

标题 ≤40 字<br>
正文 800–1500 字<br>
五段结构：引言→分析→干货→误区→互动<br>
3–5 个话题标签<br>
提交后机器审核

</td>
<td>

标题 ≤30 字<br>
正文 150–500 字<br>
必须有图（无图自动生成信息图）<br>
3–5 个 # 话题标签<br>
提交后机器审核

</td>
</tr>
</table>

### 平台智能推断规则

| 内容类型 | 自动发布到 |
|---------|-----------|
| 二手商品出售 | 闲鱼 + 小红书 |
| 干货 / 经验分享 | 小红书 + 抖音 + B站 |
| 产品推广 / 营销 | 小红书 + 抖音 |
| 深度技术文章 | B站 + 小红书 |

---

## ⚡ Hooks 系统

AmpliPost 通过 Claude Code 的 Hooks 机制在发布行为的前后各设一道拦截：

**PreToolUse Hook** 在每次调用发布脚本前触发，检查闲鱼违禁词（高仿/A货/假货/仿品/全网最低/代购）、B站和抖音的 emoji、以及极限词（全网最好/史上最/绝对最）。违禁词和 emoji 检测到则 `exit 2` 阻止执行，极限词仅输出警告不阻止。

**PostToolUse Hook** 在发布脚本执行完成后异步触发，按平台检测成功标志（小红书检测 `/publish/success`，B站检测「提交成功」，抖音检测「发布成功」或「审核中」），并将结果写入 `~/.amplipost/logs/publish_YYYYMMDD.log`。

```json
// settings.json 注册示例
{
  "hooks": {
    "PreToolUse":  [{ "matcher": "Bash", "command": "python3 .claude/hooks/pre-publish-check.py" }],
    "PostToolUse": [{ "matcher": "Bash", "command": "python3 .claude/hooks/post-publish-verify.py", "async": true }]
  }
}
```

---

## 💾 长期记忆

`memory.md` 是 AmpliPost 的持久化记忆层，由 content-coordinator 在每次任务结束后自动维护，content-reviewer 和 publish-guard 在评审时主动读取。

记忆层包含六个区块：**发帖方向演进**（有效方向与待规避方向）、**平台经验积累**（各平台有效开头/标题模式）、**发布记录**（每次发布的时间、平台、主题、状态）、**Agent 自主迭代笔记**（Agent 发现的规律和改进思路）、**用户偏好记录**（用户明确表达的风格要求）、**风控日志**（每次风控评估的决策和风险分）。

随着使用次数增加，Agent 会逐渐积累对用户偏好和平台规律的理解，内容质量和风控安全性会持续提升。

---

## 📁 项目结构

```
Amplipost/
├── CLAUDE.md                          # Claude Code 项目指令（速查表）
├── AGENTS.md                          # Multi-Agent 架构说明
├── SPEC.md                            # 完整系统规格
├── memory.md                          # 长期记忆（自动维护）
├── keys.example.txt                   # API Key 配置模板
│
├── publishers/                        # Skill 脚本（只读，仅执行发布）
│   ├── xianyu-publisher/
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   ├── xianyu_publish.py
│   │   │   ├── xianyu_publish_scrapling.py
│   │   │   └── auto_publish.py
│   │   └── references/
│   ├── xhs-publisher/
│   ├── bilibili-publisher/
│   └── douyin-publisher/
│       └── scripts/
│           └── generate_images.py     # 抖音 AI 信息图生成
│
├── .claude/
│   ├── CLAUDE.md                      # 补充指令
│   ├── settings.json                  # Hooks 注册 + 权限配置
│   ├── agents/
│   │   ├── content-coordinator.md    # 主 Agent
│   │   ├── content-reviewer.md       # 质量评审 subagent
│   │   └── publish-guard.md          # 风控守卫 subagent
│   └── hooks/
│       ├── pre-publish-check.py      # PreToolUse Hook
│       └── post-publish-verify.py    # PostToolUse Hook
│
└── tests/
    ├── test_pre_publish_check.py
    ├── test_post_publish_verify.py
    └── test_generate_images.py
```

---

## 🔧 故障排查

**登录态失效**

Agent 会主动提示需要重新扫码，扫码后 Cookie 自动更新，无需其他操作。

**内容评审连续不通过**

content-reviewer 连续 2 次评审不通过时，该平台会被跳过，最终报告中会注明「内容评审未通过」及具体原因。可以调整输入描述后重新触发。

**发布被风控拦截**

publish-guard 输出 block 决策时，报告中会说明拦截原因（通常是当日发布频率过高或内容重复度过高）。建议等待 24–48 小时后重试，或调整内容主题。

**配图中文乱码（macOS）**

```bash
brew install font-morisawa
cp $(find /usr/fonts -name "*.ttc" | head -1) ~/Library/Fonts/
```

---

## 🤝 贡献

```bash
git checkout -b feature/your-feature
git commit -m 'feat: add your feature'
git push origin feature/your-feature
# 提交 Pull Request
```

**注意：** `publishers/*/scripts/*.py` 和 `publishers/*/SKILL.md` 为只读文件，`.claude/settings.json` 已通过 `deny` 规则保护，PR 中请勿修改这些路径。

---

## 📄 许可证

[MIT License](LICENSE) · © 2025 Alan Song & Roxy Li

---

<div align="center">

[![Claude Code](https://img.shields.io/badge/Built_with-Claude_Code-8b5cf6?style=for-the-badge)](https://docs.anthropic.com/claude-code)
[![Playwright](https://img.shields.io/badge/Browser-Playwright-06b6d4?style=for-the-badge&logo=playwright)](https://playwright.dev)
[![Scrapling](https://img.shields.io/badge/Anti-Bot-Scrapling-10b981?style=for-the-badge)](https://github.com/D4Vinci/Scrapling)

*One sentence in · Four platforms out · Zero human intervention*

</div>
