import os
import time

from dataclasses import dataclass
from ollama import ChatResponse, Client
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langchain_ollama import ChatOllama


def _get_ollama_base_url() -> str:
    host = (os.getenv("OLLAMA_HOST") or "").strip()

    # Common misconfig on Windows: using 0.0.0.0 (bind-all) as a client target.
    # httpx will fail with WinError 10049 in that case.
    if host.startswith("http://") or host.startswith("https://"):
        base_url = host
    elif host:
        base_url = f"http://{host}"
    else:
        base_url = "http://127.0.0.1:11434"

    base_url = base_url.replace("0.0.0.0", "127.0.0.1")
    return base_url


def run_ai_conversation(msg: str):
    client = Client(host=_get_ollama_base_url())
    try:
        response: ChatResponse = client.chat(
            model="gemma3", messages=[{"role": "user", "content": msg}]
        )
    except Exception as e:
        print(f"Ollama request failed: {e!r}")
        raise

    msg = response.message.content
    print(msg)
    return msg


@tool
def get_weather_for_location(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


@dataclass
class Context:
    """Custom runtime context schema."""

    user_id: str


@tool
def get_user_location(runtime: ToolRuntime[Context]) -> str:
    """Retrieve user information based on user ID."""
    user_id = runtime.context.user_id
    return "Florida" if user_id == "1" else "SF"


@dataclass
class ResponseFormat:
    """Response schema for the agent."""

    punny_response: str
    weather_conditions: str | None = None


SYSTEM_PROMPT = """你是一个用于回复直播间观众弹幕的小助手，你的名字叫作小坤。

你的回答要简洁明了，不要包含过多的解释。
保持每句话的字数在40字以内，以便能在一条消息中说完。
如果回答很长，消息之间的分割尽量以40字左右为宜。
"""


def langchain_demo():
    llm = ChatOllama(model="gemma3", temperature=0, base_url=_get_ollama_base_url())

    messages = [
        ("system", SYSTEM_PROMPT),
        ("human", "小坤你是什么AI？"),
    ]
    response = llm.invoke(messages)
    print(response)

    # agent = create_agent(
    #     model="gemma3",
    #     tools=[],
    #     system_prompt=SYSTEM_PROMPT,
    # )

    # agent.run("你好")


if __name__ == "__main__":
    # print(_get_ollama_base_url())
    # run_ai_conversation("你好")
    langchain_demo()
