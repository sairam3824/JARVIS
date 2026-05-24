from app.core.config import Settings
from app.providers.openrouter_provider import OpenRouterProvider
from models.chat import ChatMessage, ChatRole


def test_build_chat_payload_keeps_tool_output_out_of_assistant_history():
    provider = OpenRouterProvider(Settings(openrouter_api_key="test-key"))

    payload = provider._build_chat_payload(
        [
            ChatMessage(role=ChatRole.USER, content="What happened?"),
            ChatMessage(role=ChatRole.TOOL, content="[weather | success]\n72F and sunny"),
        ],
        "Base system prompt",
    )

    messages = payload["messages"]

    assert messages[0]["role"] == "system"
    assert "Tool observations gathered before answering" in messages[0]["content"]
    assert "[weather | success]\n72F and sunny" in messages[0]["content"]
    assert messages[1:] == [{"role": "user", "content": "What happened?"}]
