# Lab: lab-autogen
# Module: frameworks-tools
# Doc reference: docs/frameworks-tools/autogen.md

import sys
import pathlib
import logging

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from shared.config import OPENAI_API_KEY, OPENAI_MODEL, assert_openai_key
from shared.utils import print_separator, print_section

import autogen

logging.basicConfig(level=logging.WARNING)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

LLM_CONFIG = {
    "model": OPENAI_MODEL,
    "api_key": OPENAI_API_KEY,
    "temperature": 0,
}

MAX_TURNS = 10


# ---------------------------------------------------------------------------
# Demo 1: two-agent conversation with tool execution
# ---------------------------------------------------------------------------

def search_docs(query: str) -> str:
    """Stub: search the document corpus for information."""
    corpus = {
        "hnsw": (
            "HNSW (Hierarchical Navigable Small World) builds a multi-layer graph "
            "for approximate nearest-neighbor search. Queries traverse from the top "
            "(coarse) layer down to finer layers, greedy-walking toward the target vector."
        ),
        "rate": (
            "LLM APIs enforce requests-per-minute (RPM) and tokens-per-minute (TPM) limits. "
            "When exceeded, HTTP 429 is returned. Retry with exponential backoff: "
            "delay = min(base * 2^attempt + jitter, max_delay)."
        ),
        "agent": (
            "The orchestrator-subagent pattern decomposes tasks into sub-tasks. "
            "Each subagent has isolated context — it receives only the sub-task, "
            "not the orchestrator's full history."
        ),
    }
    key = query.lower()
    for k, v in corpus.items():
        if k in key:
            return v
    return f"No results found for: {query}"


def demo_two_agent(llm_config: dict) -> None:
    print_separator("DEMO 1 — Two-agent conversation")

    # Concept: ConversableAgent — AssistantAgent is LLM-backed; answers using tools
    assistant = autogen.AssistantAgent(
        name="assistant",
        system_message=(
            "You are a technical AI assistant. Use the search_docs function to find "
            "information before answering. When the task is complete, end your "
            "response with the word TERMINATE."
        ),
        llm_config={
            **llm_config,
            "functions": [
                {
                    "name": "search_docs",
                    "description": "Search the document corpus for technical information.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query",
                            }
                        },
                        "required": ["query"],
                    },
                }
            ],
        },
    )

    # Concept: ConversableAgent — UserProxyAgent executes tools on behalf of the assistant
    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        # code_execution disabled for safety — see engineering notes in labs README
        code_execution_config=False,
        function_map={"search_docs": search_docs},
        max_consecutive_auto_reply=MAX_TURNS,
        is_termination_msg=lambda msg: "TERMINATE" in msg.get("content", ""),
    )

    task = "Search for information about HNSW and explain how it achieves fast retrieval."
    print(f"Task: {task}\n")

    # Concept: agent conversation — initiate_chat drives the conversation loop
    user_proxy.initiate_chat(assistant, message=task)

    # --------------------------------------------------
    # FAILURE CASE
    # --------------------------------------------------
    # Failure case:
    # - Remove "TERMINATE" from the assistant's system_message instruction
    # - Observe:
    #   * The conversation runs until max_consecutive_auto_reply is exhausted
    #   * No clean termination — the loop hits the ceiling rather than stopping naturally
    #   * This demonstrates why the termination signal must be explicit in the system prompt


# ---------------------------------------------------------------------------
# Demo 2: GroupChat with three specialist agents
# ---------------------------------------------------------------------------

def demo_group_chat(llm_config: dict) -> None:
    print_separator("DEMO 2 — GroupChat with three agents")

    researcher = autogen.AssistantAgent(
        name="Researcher",
        system_message=(
            "You are a research specialist. Use search_docs to find relevant information. "
            "After searching, summarize findings and pass to the Critic."
        ),
        llm_config={
            **llm_config,
            "functions": [
                {
                    "name": "search_docs",
                    "description": "Search the document corpus for technical information.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The search query"}
                        },
                        "required": ["query"],
                    },
                }
            ],
        },
    )

    critic = autogen.AssistantAgent(
        name="Critic",
        system_message=(
            "You are a technical critic. Review the Researcher's summary for accuracy "
            "and completeness. Identify any gaps. When satisfied, say APPROVED."
        ),
        llm_config=llm_config,
    )

    writer = autogen.AssistantAgent(
        name="Writer",
        system_message=(
            "You are a technical writer. Once the Critic approves, write a concise "
            "final answer. End with TERMINATE."
        ),
        llm_config=llm_config,
    )

    # Concept: GroupChat — shared transcript; GroupChatManager selects next speaker
    group_chat = autogen.GroupChat(
        agents=[researcher, critic, writer],
        messages=[],
        max_round=12,
        speaker_selection_method="auto",
    )

    manager = autogen.GroupChatManager(
        groupchat=group_chat,
        llm_config=llm_config,
    )

    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        code_execution_config=False,
        function_map={"search_docs": search_docs},
        max_consecutive_auto_reply=12,
        is_termination_msg=lambda msg: "TERMINATE" in msg.get("content", ""),
    )

    task = (
        "Research how LLM API rate limiting works and what retry strategies are recommended. "
        "Produce a final answer that a senior engineer could act on."
    )
    print(f"Task: {task}\n")
    print_section("GroupChat conversation")

    user_proxy.initiate_chat(manager, message=task)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    assert_openai_key()

    demo_two_agent(LLM_CONFIG)
    demo_group_chat(LLM_CONFIG)
