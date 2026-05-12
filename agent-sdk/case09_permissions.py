"""
Case 09: Permissions - 权限控制
=========================================

学习目标:
  - 理解不同的权限模式
  - 使用 can_use_tool 自定义权限回调
  - 在安全场景下控制 agent 行为

权限模式:
  - default:       默认，对敏感操作需要确认
  - acceptEdits:   自动接受文件编辑
  - plan:          只规划不执行
  - dontAsk:       不向用户提问
  - bypassPermissions: 跳过所有权限检查（慎用！）

运行: python case09_permissions.py
"""

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk.types import (
    AssistantMessage,
    PermissionResultAllow,
    PermissionResultDeny,
    ToolPermissionContext,
)


# ===== 自定义权限处理器 =====

async def my_permission_handler(
    tool_name: str,
    tool_input: dict,
    context: ToolPermissionContext,
) -> PermissionResultAllow | PermissionResultDeny:
    """
    自定义权限检查函数

    返回 PermissionResultAllow = 允许执行
    返回 PermissionResultDeny = 拒绝执行
    """
    # 允许所有读取操作
    if tool_name in ("Read", "Glob", "Grep"):
        print(f"  [PERMIT] {tool_name} - 读取操作，允许")
        return PermissionResultAllow()

    # 限制 Bash 命令
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        safe_prefixes = ["ls", "cat", "echo", "python", "pip", "git status"]
        for prefix in safe_prefixes:
            if command.strip().startswith(prefix):
                print(f"  [PERMIT] Bash: {command[:50]} - 安全命令，允许")
                return PermissionResultAllow()
        print(f"  [DENY] Bash: {command[:50]} - 非白名单命令，拒绝")
        return PermissionResultDeny(message=f"非白名单命令被拒绝: {command[:50]}")

    # 拒绝所有写操作
    if tool_name in ("Write", "Edit"):
        print(f"  [DENY] {tool_name} - 写操作被禁止")
        return PermissionResultDeny(message=f"{tool_name} 写操作被禁止")

    # 其他工具默认允许
    print(f"  [PERMIT] {tool_name} - 默认允许")
    return PermissionResultAllow()


async def main():
    # ===== 方式 1: 使用自定义权限回调 =====
    print("===== 方式 1: 自定义权限回调 =====\n")

    options = ClaudeAgentOptions(
        system_prompt="你是一个助手，可以帮助查看文件和执行命令。",
        allowed_tools=["Read", "Bash", "Glob"],
        can_use_tool=my_permission_handler,
    )

    # can_use_tool 需要 streaming 模式，使用 AsyncIterable 作为 prompt
    async def prompt_iter():
        yield {"type": "user", "message": {"role": "user", "content": "帮我看看当前目录有哪些 Python 文件，并查看 case01 的内容。"}}

    async for message in query(
        prompt=prompt_iter(),
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text[:300])

    # ===== 方式 2: bypassPermissions 模式 =====
    print("\n\n===== 方式 2: bypassPermissions 模式 =====\n")
    print("(跳过所有权限检查，适用于受信任的自动化场景)")

    options_bypass = ClaudeAgentOptions(
        system_prompt="你是一个助手。",
        allowed_tools=["Bash"],
        permission_mode="bypassPermissions",
    )

    async for message in query(
        prompt="帮我查看当前日期。",
        options=options_bypass,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text[:300])

    print("\n注意: bypassPermissions 在生产环境中请谨慎使用！")


if __name__ == "__main__":
    asyncio.run(main())
