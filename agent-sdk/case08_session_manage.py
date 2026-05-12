"""
Case 08: Session Management - 会话管理
=========================================

学习目标:
  - 使用 resume 参数恢复历史会话
  - 管理 session 生命周期
  - 查看历史消息

应用场景:
  - 用户关闭浏览器后恢复对话
  - 从某个关键节点创建分支探索不同方案
  - 查看和回顾历史会话

运行: python case08_session_manage.py
"""

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, list_sessions, get_session_messages
from claude_agent_sdk.types import AssistantMessage, ResultMessage


async def main():
    options = ClaudeAgentOptions(
        system_prompt="你是一个有帮助的助手，请用中文回答。",
        tools=[],
    )

    # ===== 1. 创建初始会话 =====
    print("===== 步骤 1: 创建会话 =====")
    session_id = None
    async for message in query(
        prompt="我正在规划一次日本旅行，帮我列 3 个必去的城市。",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text[:300])
        elif isinstance(message, ResultMessage):
            session_id = message.session_id

    print(f"\nsession_id: {session_id}")

    # ===== 2. 恢复会话，继续对话 =====
    print("\n===== 步骤 2: 恢复会话继续对话 =====")
    # 使用 resume 参数恢复上下文
    resume_options = ClaudeAgentOptions(
        system_prompt="你是一个有帮助的助手，请用中文回答。",
        tools=[],
        resume=session_id,
    )

    async for message in query(
        prompt="针对你提到的第一个城市，给我一个 3 天的行程安排。",
        options=resume_options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text[:300])

    # ===== 3. 列出所有会话 =====
    print("\n===== 步骤 3: 列出会话 =====")
    sessions = list_sessions()
    print(f"总会话数: {len(sessions)}")
    for s in sessions[-3:]:  # 只看最近 3 个
        print(f"  - {s}")

    # ===== 4. 获取会话历史消息 =====
    print("\n===== 步骤 4: 查看历史消息 =====")
    if session_id:
        messages = get_session_messages(session_id=session_id)
        print(f"消息数: {len(messages)}")
        for msg in messages:
            print(f"  [{msg.type}] ", end="")
            if hasattr(msg, "message") and hasattr(msg.message, "content"):
                for block in msg.message.content:
                    if hasattr(block, "text"):
                        print(block.text[:80])
                        break


if __name__ == "__main__":
    asyncio.run(main())
