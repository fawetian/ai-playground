"""
Case 02: System Prompt - 自定义系统提示词
=========================================

学习目标:
  - 使用 ClaudeAgentOptions 配置 agent
  - 自定义 system_prompt 控制行为
  - 限制 tools 控制可用工具

运行: python case02_system_prompt.py
"""

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk.types import AssistantMessage


async def main():
    # ClaudeAgentOptions 允许你对 agent 做各种配置
    options = ClaudeAgentOptions(
        # system_prompt 定义 agent 的角色和行为准则
        system_prompt=(
            "你是一个资深的 Python 代码审查专家。"
            "你的任务是：\n"
            "1. 审查用户提供的代码\n"
            "2. 指出潜在问题（bug、性能、安全）\n"
            "3. 给出改进建议\n"
            "请用中文回复，格式使用 markdown。"
        ),
        # tools=[] = 纯对话模式，不使用任何内置工具
        tools=[],
    )

    async for message in query(
        prompt=(
            "请审查这段代码：\n\n"
            "```python\n"
            "def get_user(id):\n"
            "    import sqlite3\n"
            "    conn = sqlite3.connect('db.sqlite')\n"
            "    cursor = conn.cursor()\n"
            "    cursor.execute(f'SELECT * FROM users WHERE id = {id}')\n"
            "    return cursor.fetchone()\n"
            "```\n"
        ),
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text)


if __name__ == "__main__":
    asyncio.run(main())
