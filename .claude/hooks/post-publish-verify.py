#!/usr/bin/env python3
"""
PostToolUse hook — 发布后结果验证与日志记录

Claude Code 规范：
- 输入：stdin 读取 JSON（含 tool_response）
- exit 0 → 始终，PostToolUse 不阻止操作
- 副作用：写入本地日志
"""

import json
import os
import sys
from datetime import datetime, timezone

SUCCESS_PATTERNS = {
    "xhs_publish":      "/publish/success",
    "bilibili_publish": "提交成功",
    "douyin_publish":   "发布成功",  # 也接受「审核中」
}

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    tool_response = data.get("tool_response", {})

    if tool_name != "Bash":
        sys.exit(0)

    command = tool_input.get("command", "")
    stdout = tool_response.get("stdout", "")
    exit_code = tool_response.get("exit_code", -1)

    # 只处理发布脚本
    publish_scripts = ["xianyu_publish", "xhs_publish", "bilibili_publish", "douyin_publish"]
    matched = next((s for s in publish_scripts if s in command), None)
    if not matched:
        sys.exit(0)

    # 判断发布结果
    platform_map = {
        "xianyu_publish":   "xianyu",
        "xhs_publish":      "xhs",
        "bilibili_publish":  "bilibili",
        "douyin_publish":   "douyin",
    }
    platform = platform_map[matched]

    if platform == "xianyu":
        success = exit_code == 0
    elif platform == "douyin":
        success = "发布成功" in stdout or "审核中" in stdout
    else:
        pattern = SUCCESS_PATTERNS.get(matched, "")
        success = pattern in stdout

    # 写日志
    log_dir = os.path.expanduser("~/.amplipost/logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"publish_{datetime.now().strftime('%Y%m%d')}.log")
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(log_file, "a") as f:
        f.write(f"[{ts}] platform={platform} success={success} exit_code={exit_code}\n")

    sys.exit(0)

if __name__ == "__main__":
    main()
