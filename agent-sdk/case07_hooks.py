"""
Case 07: Hooks - 钩子系统
=========================================

学习目标:
  - 理解 Hooks 的作用和触发时机
  - 使用 HookMatcher 匹配特定工具调用
  - 实现 PreToolUse / PostToolUse 钩子

Hooks 是 Agent SDK 的"中间件"机制：
  - PreToolUse:    工具执行前触发（可以阻止执行）
  - PostToolUse:   工具执行后触发（可以记录日志）
  - UserPromptSubmit: 用户发送消息时触发
  - Stop:           agent 停止时触发

运行: python case07_hooks.py
"""

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, HookMatcher
from claude_agent_sdk.types import AssistantMessage


# ===== PreToolUse 钩子 =====

async def log_before_tool(context, stdout, hook_context):
    """工具执行前记录日志"""
    tool_name = context.get("tool_name", "unknown")
    tool_input = context.get("tool_input", {})
    print(f"  [PreToolUse] 即将执行: {tool_name}")
    print(f"  [PreToolUse] 参数: {tool_input}")
    return None  # 返回 None = 允许执行


async def block_dangerous_commands(context, stdout, hook_context):
    """阻止危险的 Bash 命令"""
    tool_input = context.get("tool_input", {})
    command = tool_input.get("command", "")
    dangerous = ["rm -rf", "drop table", "delete from", "format"]
    for d in dangerous:
        if d in command.lower():
            print(f"  [BLOCKED] 检测到危险命令: {command}")
            return {"decision": "block", "reason": f"危险命令被阻止: {command}"}
    return None


# ===== PostToolUse 钩子 =====

async def log_after_tool(context, stdout, hook_context):
    """工具执行后记录日志"""
    tool_name = context.get("tool_name", "unknown")
    print(f"  [PostToolUse] 已完成: {tool_name}")
    return None


async def main():
    options = ClaudeAgentOptions(
        system_prompt="你是一个助手，可以执行 Bash 命令来帮助用户。",
        allowed_tools=["Bash"],
        hooks={
            "PreToolUse": [
                # 匹配所有工具 - 记录日志
                HookMatcher(hooks=[log_before_tool]),
                # 专门匹配 Bash - 拦截危险命令
                HookMatcher(matcher="Bash", hooks=[block_dangerous_commands]),
            ],
            "PostToolUse": [
                # 记录工具执行完成
                HookMatcher(hooks=[log_after_tool]),
            ],
        },
        permission_mode="bypassPermissions",
    )

    print("===== 测试 1: 正常命令 =====")
    async for message in query(
        prompt="帮我查看当前日期和时间。",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(f"\n{block.text}")

    print("\n\n===== 测试 2: 尝试危险命令 =====")
    async for message in query(
        prompt="帮我执行 rm -rf /tmp/test 目录。",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(f"\n{block.text}")


if __name__ == "__main__":
    asyncio.run(main())
