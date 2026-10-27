import asyncio
import json
import sys
from pathlib import Path

import requests
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

API_URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:1.5b"
MAX_ROUNDS = 5

SYSTEM_PROMPT = """
You are Kleos, an AI DevOps Chatbot Assistant.

Answer general DevOps questions clearly and concisely.
Use the available MCP tools to retrieve real project and GitHub data.

Tool selection rules:
- For GitHub Actions workflow history or run status, call get_github_workflow_runs.
- For jobs, individual steps, or failed steps in a specific run, call get_github_run_jobs with its run_id.
- When asked to inspect, analyze, or classify GitHub Actions job logs, warnings, errors, or false positives, call get_github_job_log_findings with the supplied job_id.
- Do not refuse a GitHub log inspection request before trying the relevant available tool.
- After receiving tool results, explain what the results actually show.
- Distinguish genuine warnings from keyword-match false positives.
- Do not claim a warning caused a failure unless the evidence supports that conclusion.
- Never claim a tool ran unless its result confirms it.
- If a tool returns an error or insufficient data, explain that honestly.
- Never invent tool results or pretend to have access beyond the returned data.
"""


def ask_ollama(messages, tools):
    response = requests.post(
        API_URL,
        json={
            "model": MODEL,
            "stream": False,
            "messages": messages,
            "tools": tools,
        },
        timeout=180,
    )
    response.raise_for_status()
    return response.json()["message"]


def convert_mcp_tools(mcp_tools):
    ollama_tools = []

    for tool in mcp_tools:
        ollama_tools.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.inputSchema or {
                    "type": "object",
                    "properties": {},
                },
            },
        })

    return ollama_tools


def format_tool_result(result):
    content = []

    for item in result.content:
        if hasattr(item, "text"):
            content.append(item.text)

    if result.isError:
        return json.dumps({"error": "\n".join(content)})

    if content:
        return "\n".join(content)

    return json.dumps({"result": "Tool executed without text output"})


async def main():
    server = StdioServerParameters(
        command=sys.executable,
        args=[str(Path(__file__).resolve().parent / "mcp_server.py")],
    )

    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            mcp_tools = (await session.list_tools()).tools
            tools = convert_mcp_tools(mcp_tools)

            print("Kleos is ready.")
            print("Available MCP tools:")
            for tool in mcp_tools:
                print(f"- {tool.name}")
            print("Type 'exit' to quit.\n")

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]

            while True:
                try:
                    user_input = input("You: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\nKleos stopped.")
                    break

                if not user_input:
                    continue

                if user_input.lower() in {"exit", "quit"}:
                    print("Kleos stopped.")
                    break

                messages.append({
                    "role": "user",
                    "content": user_input,
                })

                for round_number in range(1, MAX_ROUNDS + 1):
                    try:
                        assistant_message = await asyncio.to_thread(
                            ask_ollama, messages, tools
                        )
                    except Exception as error:
                        print(f"\nAI request failed: {error}\n")
                        messages.pop()
                        break

                    messages.append(assistant_message)
                    tool_calls = assistant_message.get("tool_calls", [])

                    if not tool_calls:
                        print(
                            "\nKleos:",
                            assistant_message.get("content", ""),
                            "\n",
                        )
                        break

                    print(
                        f"\nAgent round {round_number}: "
                        f"{len(tool_calls)} tool call(s)"
                    )

                    for call in tool_calls:
                        function = call.get("function", {})
                        name = function.get("name", "")
                        arguments = function.get("arguments", {})

                        if isinstance(arguments, str):
                            try:
                                arguments = json.loads(arguments)
                            except json.JSONDecodeError:
                                arguments = {}

                        try:
                            result = await session.call_tool(
                                name, arguments
                            )
                            output = format_tool_result(result)
                        except Exception as error:
                            output = json.dumps({"error": str(error)})

                        print(f"Executed: {name}")

                        messages.append({
                            "role": "tool",
                            "content": output,
                        })
                else:
                    print(
                        "\nKleos stopped: reached the "
                        f"{MAX_ROUNDS}-round limit.\n"
                    )


if __name__ == "__main__":
    asyncio.run(main())
