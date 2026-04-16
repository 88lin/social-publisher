---
name: amplipost-workflow
description: Amplipost 多平台内容发布工作流规范。当用户触发任何内容发布需求时加载，提供完整的发布流程指南和合规规则。触发词：发布内容、多平台发布、营销推广、发闲鱼、发小红书、发B站、发抖音、一键发布、批量发布。
---

# Amplipost 发布工作流规范

## 快速参考

### 平台脚本调用

```bash
# 闲鱼
python3 ~/.openclaw/skills/xianyu-publisher/scripts/xianyu_publish.py \
  --title "【95新】商品名称" --price "999" --new-degree "95新" \
  [--description "描述"] [--image "/path/to/img.jpg"]

# 小红书（文字配图）
python3 ~/.openclaw/skills/xhs-publisher/scripts/xhs_publish.py \
  --title "标题≤20字" --content "正文200-300字"

# 小红书（上传图片）
python3 ~/.openclaw/skills/xhs-publisher/scripts/xhs_publish.py \
  --title "标题" --content "正文" --image "/path/to/img.png"

# B站专栏
python3 ~/.openclaw/skills/bilibili-publisher/scripts/bilibili_publish.py \
  --title "标题≤40字" --content "正文800-1500字" \
  [--tags "标签1,标签2,标签3"]

# 抖音图文（自动配图）
python3 ~/.openclaw/skills/douyin-publisher/scripts/douyin_publish.py \
  --title "标题≤30字" --content "正文150-500字" --auto-generate

# 抖音图文（上传图片）
python3 ~/.openclaw/skills/douyin-publisher/scripts/douyin_publish.py \
  --title "标题" --content "正文" --images "img1.jpg,img2.jpg"
```

### 备用路径（openclaw 路径不存在时）

```bash
XIANYU=publishers/xianyu-publisher/scripts/xianyu_publish.py
XHS=publishers/xhs-publisher/scripts/xhs_publish.py
BILIBILI=publishers/bilibili-publisher/scripts/bilibili_publish.py
DOUYIN=publishers/douyin-publisher/scripts/douyin_publish.py
```

---

## 发布前必做检查

### 通用检查
- [ ] 标题长度符合平台限制
- [ ] 正文字数在规定范围内
- [ ] 无极限词（最好/第一/绝对/最低）
- [ ] 无虚假数据

### 平台特定检查
- [ ] **闲鱼**：违禁词已替换，价格和新旧程度已填写
- [ ] **B站/抖音**：无任何 emoji 或 Unicode 表情
- [ ] **抖音**：图片路径有效或使用 --auto-generate

### 登录态检查
```bash
# 检查 profile 目录是否存在（存在则已登录）
ls ~/.openclaw/browser_profiles/xianyu_default/  # 闲鱼
ls ~/.catpaw/xhs_browser_profile/                 # 小红书
ls ~/.catpaw/bilibili_browser_profile/            # B站
ls ~/.catpaw/douyin_browser_profile/              # 抖音
```

---

## 内容合规规则

### 闲鱼违禁词替换表
| 违禁词 | 替换词 |
|--------|--------|
| 高仿 | 复刻 |
| A货 | 正品 |
| 全网最低 | 优惠价 |
| 假货 | 特价商品 |
| 仿品 | 同款 |
| 代购 | 自购 |

### 所有平台极限词（禁止使用）
最好、第一、最低、最高、绝对、全网、史上、超越一切

### B站/抖音 emoji 禁止
正文和标题中禁止任何 emoji（😀🎉等）和 Unicode 表情符号

---

## 发布顺序建议（多平台时）

1. **闲鱼** - 商品类，直接发布，无审核
2. **小红书** - 直接发布，无审核
3. **抖音** - 进入机器审核（通常数分钟到数小时）
4. **B站** - 进入机器审核（通常数分钟到数小时）

每个平台发布后等待 **15 秒**再发下一个，避免平台判定重复内容。

---

## 故障排除

### 登录失效
```
提示用户：请在浏览器中重新登录 {平台}，登录后再重试发布
```

### 脚本不存在
```bash
# 检查 openclaw skill 是否安装
ls ~/.openclaw/skills/

# 如未安装，提示用户安装
echo "请安装 {platform}-publisher skill"
```

### 发布失败重试
```bash
# 等待 30 秒后重试
sleep 30
python3 "$SCRIPT" [原始参数]
```

### 中文配图乱码（macOS）
```bash
# 检查字体
ls /System/Library/Fonts/ | grep -i heit
# STHeiti Light.ttc 应该存在
```
