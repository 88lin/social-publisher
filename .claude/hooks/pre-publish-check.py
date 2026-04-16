#!/usr/bin/env python3
"""
PreToolUse hook — 发布前合规检查

Claude Code 规范：
- 输入：stdin 读取 JSON
- 输出：stdout 输出 JSON（可选）
- exit 0 → 通过，继续执行
- exit 2 → 阻止，stderr 内容作为错误原因传给 Claude
- exit 1 → 非阻止错误，记录但继续
"""

import json
import re
import sys

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # 无法解析则放行

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    # 只处理 Bash 工具
    if tool_name != "Bash":
        sys.exit(0)

    command = tool_input.get("command", "")

    # 只处理发布脚本调用
    publish_scripts = ["xianyu_publish", "xhs_publish", "bilibili_publish", "douyin_publish"]
    if not any(s in command for s in publish_scripts):
        sys.exit(0)

    # --- 检查1：闲鱼违禁词 ---
    if "xianyu_publish" in command:
        banned = {
            "高仿": "复刻",
            "A货": "正品",
            "全网最低": "优惠价",
            "假货": "特价商品",
            "仿品": "同款",
        }
        for word, replacement in banned.items():
            if word in command:
                print(
                    f"检测到闲鱼违禁词「{word}」，请替换为「{replacement}」后重试",
                    file=sys.stderr,
                )
                sys.exit(2)  # 阻止执行

    # --- 检查2：B站/抖音 emoji ---
    if "bilibili_publish" in command or "douyin_publish" in command:
        emoji_pattern = re.compile(
            "[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0001FA00-\U0001FA9F]",
            re.UNICODE,
        )
        if emoji_pattern.search(command):
            print(
                "B站/抖音内容不允许 emoji，请移除后重试",
                file=sys.stderr,
            )
            sys.exit(2)  # 阻止执行

    # --- 检查3：极限词（警告，不阻止）---
    extreme_words = ["全网最好", "全网第一", "史上最", "绝对最"]
    for word in extreme_words:
        if word in command:
            # exit 0 + stdout JSON 传 warning 给 Claude
            result = {
                "continue": True,
                "suppressOutput": False,
                "hookSpecificOutput": {
                    "additionalContext": f"警告：命令中包含极限词「{word}」，建议修改但不强制阻止。"
                }
            }
            print(json.dumps(result, ensure_ascii=False))
            sys.exit(0)

    sys.exit(0)  # 通过

if __name__ == "__main__":
    main()
