"""
Case 10: Subagents - 子代理系统
=========================================

学习目标:
  - 使用 AgentDefinition 定义子代理
  - 为子代理分配专门的 prompt 和工具
  - 实现多代理协作

Subagents 允许你创建"专家团队"：
  - 主 agent 像项目经理，协调各个子代理
  - 每个子代理有专属的 prompt 和工具
  - 主 agent 根据任务类型分派给合适的子代理

运行: python case10_subagents.py
"""

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition, tool, create_sdk_mcp_server
from claude_agent_sdk.types import AssistantMessage


# ===== 定义子代理专属工具 =====

@tool("security_scan", "分析代码的安全性问题", {"code": str})
async def security_scan(args):
    """扫描代码中的安全问题"""
    code = args["code"]
    issues = []
    if "eval(" in code:
        issues.append("高危: 使用了 eval()，存在代码注入风险")
    if "SELECT" in code and "{" in code:
        issues.append("高危: 可能存在 SQL 注入")
    if "password" in code.lower() and "=" in code:
        issues.append("中危: 疑似硬编码密码")
    if not issues:
        result = "扫描完成: 未发现明显安全问题"
    else:
        result = "扫描完成:\n" + "\n".join(f"- {i}" for i in issues)
    return {"content": [{"type": "text", "text": result}]}


@tool("performance_check", "分析代码的性能问题", {"code": str})
async def performance_check(args):
    """检查代码性能问题"""
    code = args["code"]
    issues = []
    if "for" in code and "append" in code:
        issues.append("提示: 考虑使用列表推导式替代循环 append")
    if "import re" in code and "re.compile" not in code:
        issues.append("提示: 频繁使用的正则建议预编译")
    if "sleep(" in code:
        issues.append("警告: 使用了 sleep()，可能影响性能")
    if not issues:
        result = "检查完成: 未发现明显性能问题"
    else:
        result = "检查完成:\n" + "\n".join(f"- {i}" for i in issues)
    return {"content": [{"type": "text", "text": result}]}


async def main():
    # ===== 定义子代理 =====

    # 子代理 1: 安全审查专家
    security_mcp = create_sdk_mcp_server(
        name="security_tools",
        tools=[security_scan],
    )
    security_agent = AgentDefinition(
        description="代码安全审查专家，擅长发现 SQL 注入、XSS、代码注入等安全问题。",
        prompt=(
            "你是代码安全审查专家。"
            "当用户提交代码时，使用 security_scan 工具分析安全问题。"
            "给出详细的安全报告和修复建议。请用中文回复。"
        ),
        mcpServers=["security_tools"],
    )

    # 子代理 2: 性能优化专家
    perf_mcp = create_sdk_mcp_server(
        name="perf_tools",
        tools=[performance_check],
    )
    perf_agent = AgentDefinition(
        description="代码性能优化专家，擅长发现性能瓶颈并给出优化建议。",
        prompt=(
            "你是代码性能优化专家。"
            "当用户提交代码时，使用 performance_check 工具分析性能问题。"
            "给出详细的优化建议。请用中文回复。"
        ),
        mcpServers=["perf_tools"],
    )

    # ===== 主 Agent 配置 =====
    options = ClaudeAgentOptions(
        system_prompt=(
            "你是代码审查协调员。根据用户的需求，"
            "委派给合适的子代理处理：\n"
            "- 安全问题 → security-reviewer\n"
            "- 性能问题 → performance-reviewer\n"
            "- 综合审查 → 同时调用两个子代理\n"
            "请用中文回复。"
        ),
        mcp_servers={
            "security_tools": security_mcp,
            "perf_tools": perf_mcp,
        },
        agents={
            "security-reviewer": security_agent,
            "performance-reviewer": perf_agent,
        },
        permission_mode="bypassPermissions",
    )

    # ===== 测试 =====
    test_code = '''
def login(username, password):
    import sqlite3
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    cursor.execute(query)
    result = cursor.fetchone()
    if result:
        eval(f"print('Welcome {username}')")
    return result
'''

    print("===== 综合代码审查 =====\n")
    async for message in query(
        prompt=f"请对以下代码进行综合审查（安全和性能）：\n```\n{test_code}\n```",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text)


if __name__ == "__main__":
    asyncio.run(main())
