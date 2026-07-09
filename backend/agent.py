import json
import os
import tiktoken
from groq import Groq
from tools import TOOLS, execute_tool

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
enc = tiktoken.get_encoding("cl100k_base")

MODEL = "llama-3.1-8b-instant"
MAX_CONTEXT_TOKENS = 10000
MAX_STEPS = 5


def count_tokens(messages: list) -> int:
    total = 0
    for msg in messages:
        content = msg.get("content", "")
        if isinstance(content, str):
            total += len(enc.encode(content))
    return total


def summarise_history(messages: list) -> str:
    conversation = "\n".join([
        f"{m['role'].upper()}: {m['content']}"
        for m in messages
        if isinstance(m.get("content"), str) and m["role"] != "system"
    ])
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{
            "role": "user",
            "content": f"Summarise this conversation in 3-4 sentences, keeping all key facts and answers:\n\n{conversation}"
        }],
        max_tokens=200
    )
    return response.choices[0].message.content


def trim_context(messages: list):
    total = count_tokens(messages)
    if total < MAX_CONTEXT_TOKENS:
        return messages, None

    system_msgs = [m for m in messages if m["role"] == "system"]
    non_system  = [m for m in messages if m["role"] != "system"]
    older  = non_system[:-5] if len(non_system) > 5 else []
    recent = non_system[-5:]

    if not older:
        return messages, None

    summary = summarise_history(older)
    trimmed = system_msgs + [
        {"role": "system", "content": f"Summary of earlier conversation: {summary}"}
    ] + recent

    return trimmed, summary


def run_agent(question: str, conversation_history: list):
    system_prompt = {
        "role": "system",
        "content": """You are an intelligent AI research assistant with access to tools.
Use tools when needed to find accurate information.
Always think step by step.
Cite which tools you used in your final answer.
Be concise but complete."""
    }

    messages = [system_prompt] + conversation_history + [
        {"role": "user", "content": question}
    ]

    messages, summary = trim_context(messages)

    steps = []
    step_count = 0

    while step_count < MAX_STEPS:
        step_count += 1

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=512
        )

        msg = response.choices[0].message
        finish_reason = response.choices[0].finish_reason

        if finish_reason == "stop":
            return {
                "answer": msg.content,
                "steps": steps,
                "context_summary": summary,
                "total_steps": step_count,
                "tokens_used": count_tokens(messages)
            }

        if finish_reason == "tool_calls" and msg.tool_calls:
            tool_call_data = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in msg.tool_calls
            ]

            messages.append({
                "role": "assistant",
                "content": msg.content,
                "tool_calls": tool_call_data
            })

            for tc in msg.tool_calls:
                try:
                    tool_name  = tc.function.name
                    tool_input = json.loads(tc.function.arguments)
                    result     = execute_tool(tool_name, tool_input)
                except Exception as e:
                    tool_name  = tc.function.name if hasattr(tc, "function") else "unknown"
                    tool_input = {}
                    result     = f"Tool error: {str(e)}"

                steps.append({
                    "step": step_count,
                    "tool": tool_name,
                    "input": tool_input,
                    "result": result
                })

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result
                })

    return {
        "answer": "Maximum steps reached. Here is what I found so far.",
        "steps": steps,
        "context_summary": summary,
        "total_steps": step_count,
        "tokens_used": count_tokens(messages)
    }
