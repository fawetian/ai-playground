"""Test if Claude Agent SDK works with current env config."""
import asyncio
import os
from claude_agent_sdk import query
from claude_agent_sdk.types import ClaudeAgentOptions


async def main():
    print(f"ANTHROPIC_API_KEY: {'SET' if os.environ.get('ANTHROPIC_API_KEY') else 'NOT SET'}")
    print(f"ANTHROPIC_BASE_URL: {os.environ.get('ANTHROPIC_BASE_URL', 'NOT SET')}")
    print()

    if not os.environ.get("ANTHROPIC_API_KEY") and os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        os.environ["ANTHROPIC_API_KEY"] = os.environ["ANTHROPIC_AUTH_TOKEN"]
        print("Copied ANTHROPIC_AUTH_TOKEN -> ANTHROPIC_API_KEY")

    print("\nSending test query...")

    options = ClaudeAgentOptions(
        env={
            "ANTHROPIC_API_KEY": os.environ["ANTHROPIC_API_KEY"],
        },
    )
    if os.environ.get("ANTHROPIC_BASE_URL"):
        options.env["ANTHROPIC_BASE_URL"] = os.environ["ANTHROPIC_BASE_URL"]

    async for message in query(
        prompt="Say hello in one sentence.",
        options=options,
    ):
        print(f"\n[Message type: {type(message).__name__}]")
        if hasattr(message, "content"):
            for block in message.content:
                if hasattr(block, "text"):
                    print(f"  {block.text}")
        if hasattr(message, "result"):
            print(f"  result: {message.result}")


if __name__ == "__main__":
    asyncio.run(main())
