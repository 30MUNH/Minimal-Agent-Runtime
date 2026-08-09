import json
import unittest

from agent_runtime import ModelReply
from agent_runtime.models import OpenAIModelProvider


class FakeOpenAIResponse:
    def __init__(self, output):
        self.output = output


class FakeOutputItem:
    def __init__(self, item_type, **kwargs):
        self.type = item_type
        self.name = kwargs.get("name")
        self.arguments = kwargs.get("arguments")
        self.call_id = kwargs.get("call_id")
        self.content = kwargs.get("content")


class FakeResponses:
    def __init__(self, output):
        self.output = output
        self.kwargs = None

    def create(self, **kwargs):
        self.kwargs = kwargs
        return FakeOpenAIResponse(self.output)


class FakeClient:
    def __init__(self, output):
        self.responses = FakeResponses(output)


class OpenAIProviderTests(unittest.TestCase):
    def test_openai_provider_sends_messages_and_tools_and_normalizes_tool_call(self):
        client = FakeClient([FakeOutputItem("function_call", name="search_files", arguments=json.dumps({"query": "TODO"}), call_id="call_123")])
        provider = OpenAIModelProvider(client=client, model="test-model")

        reply = provider.complete(
            messages=[{"role": "user", "content": "Find TODOs"}],
            tools=[{"name": "search_files", "description": "Search.", "schema": {"type": "object"}}],
        )

        self.assertEqual(reply, ModelReply.tool_call("search_files", {"query": "TODO"}, call_id="call_123"))
        self.assertEqual(client.responses.kwargs["model"], "test-model")
        self.assertEqual(client.responses.kwargs["input"], [{"role": "user", "content": "Find TODOs"}])
        self.assertEqual(client.responses.kwargs["tools"][0]["name"], "search_files")

    def test_openai_provider_normalizes_text_final_answer(self):
        client = FakeClient([FakeOutputItem("message", content=[{"type": "output_text", "text": "Done"}])])
        provider = OpenAIModelProvider(client=client, model="test-model")

        reply = provider.complete(messages=[], tools=[])

        self.assertEqual(reply, ModelReply.final("Done"))
