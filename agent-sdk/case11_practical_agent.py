"""
Case 11: Practical Example - 实战项目助手
=========================================

学习目标:
  - 综合运用 SDK 所有核心特性
  - 构建一个实用的"项目助手" agent
  - 体验真实场景下的 agent 开发

这个 agent 可以:
  - 分析项目结构
  - 搜索代码
  - 执行命令
  - 回答关于项目的问题

运行: python case11_practical_agent.py
"""

import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, tool, create_sdk_mcp_server
from claude_agent_sdk.types import AssistantMessage


# ===== 项目助手工具 =====

@tool("project_info", "获取项目的基本信息", {})
async def project_info(args):
    """返回当前项目的信息"""
    return {
        "content": [
            {
                "type": "text",
                "text": (
                    "项目: ai-playground\n"
                    "类型: Python 学习项目\n"
                    "位置: /Users/zhihu/code/m_code/ai/ai-playground\n"
                    "目录: 包含多个学习案例子目录"
                ),
            }
        ]
    }


@tool("list_cases", "获取当前可用的学习案例列表", {})
async def list_cases(args):
    """列出所有学习案例"""
    cases = [
        ("case01", "Hello Query - 最基础的 SDK 调用"),
        ("case02", "System Prompt - 自定义系统提示词"),
        ("case03", "Built-in Tools - 使用内置工具"),
        ("case04", "Client Session - 多轮连续对话"),
        ("case05", "Custom Tools - 自定义工具"),
        ("case06", "Streaming - 流式输出"),
        ("case07", "Hooks - 钩子系统"),
        ("case08", "Session Management - 会话管理"),
        ("case09", "Permissions - 权限控制"),
        ("case10", "Subagents - 子代理系统"),
        ("case11", "Practical Example - 实战项目助手"),
    ]
    return {
        "content": [
            {
                "type": "text",
                "text": "\n".join(f"  {name}: {desc}" for name, desc in cases),
            }
        ]
    }


@tool("get_case_summary", "获取指定案例的学习要点", {"case_name": str})
async def get_case_summary(args):
    """获取案例的学习要点"""
    case_name = args["case_name"]
    summaries = {
        "case01": "学习 query() 基本用法、返回类型 ResultMessage、ContentBlock",
        "case02": "学习 ClaudeAgentOptions 配置、system_prompt、tools",
        "case03": "学习内置工具（Read/Write/Edit/Bash/Glob/Grep/WebSearch）、ToolUseBlock",
        "case04": "学习 ClaudeSDKClient 多轮对话、上下文保持、receive_response",
        "case05": "学习 @tool 装饰器、create_sdk_mcp_server、MCP 工具注册",
        "case06": "学习 streaming 模式、AsyncIterator 处理、实时输出",
        "case07": "学习 Hooks 系统（PreToolUse/PostToolUse）、HookMatcher",
        "case08": "学习 resume 恢复会话、list_sessions、get_session_messages",
        "case09": "学习权限模式、can_use_tool 回调、安全控制",
        "case10": "学习 AgentDefinition、子代理协作、多专家系统",
        "case11": "综合运用所有特性，构建完整 agent",
    }
    result = summaries.get(
        case_name,
        f"未找到案例 {case_name}，可用案例: case01-case11",
    )
    return {"content": [{"type": "text", "text": result}]}


async def main():
    # 创建 MCP 服务器
    mcp_server = create_sdk_mcp_server(
        name="project_assistant",
        tools=[project_info, list_cases, get_case_summary],
    )

    # 创建持续会话的 client
    options = ClaudeAgentOptions(
        system_prompt=(
            "你是 Claude Agent SDK 学习助手。你可以：\n"
            "1. 介绍 Agent SDK 的概念和特性\n"
            "2. 列出所有学习案例\n"
            "3. 解释每个案例的学习要点\n"
            "4. 回答关于 SDK 的问题\n"
            "请用中文回答，尽量简洁明了。"
        ),
        mcp_servers={"project_assistant": mcp_server},
        allowed_tools=["project_info", "list_cases", "get_case_summary"],
        permission_mode="bypassPermissions",
    )

    async with ClaudeSDKClient(options=options) as client:
        print("Claude Agent SDK 学习助手")
        print("输入 'quit' 退出\n")

        # 交互式对话循环
        while True:
            try:
                user_input = input("你: ").strip()
            except (EOFError, KeyboardInterrupt):
                break

            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit", "q"):
                break

            await client.query(user_input)

            print("\n助手: ", end="")
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if hasattr(block, "text"):
                            print(block.text)
            print()

    print("\n再见！")


if __name__ == "__main__":
    asyncio.run(main())
