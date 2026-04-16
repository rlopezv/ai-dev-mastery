# Lab: lab-agent-patterns
# Module: ai-agents
# Doc reference: docs/ai-agents/agent-patterns.md

import sys
import pathlib
import logging

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from shared.config import MODEL, MAX_ITERATIONS, build_client, assert_ollama_ready
from shared.dispatcher import InlineDispatcher
from shared.loop import run_agent
from shared.tools import search_web, read_document

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for articles about a topic. Returns document IDs and titles.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"},
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_document",
            "description": "Read the full content of a document by its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "Document ID from search results"},
                },
                "required": ["document_id"],
                "additionalProperties": False,
            },
        },
    },
]

DISPATCHER = InlineDispatcher(
    {
        "search_web": search_web,
        "read_document": read_document,
    }
)

RESEARCH_TASK = (
    "Search for papers about the ReAct agent pattern, read the most relevant one, "
    "and write a one-sentence summary of its key contribution."
)


# ---------------------------------------------------------------------------
# Demo 1: ReAct pattern
# ---------------------------------------------------------------------------

# Concept: ReAct pattern — system prompt enforces Thought/Action/Observation structure
REACT_SYSTEM = (
    "You are a research assistant. You MUST follow this exact format for every step:\n\n"
    "Thought: [what you know and what you need next]\n"
    "Action: [call a tool]\n"
    "Observation: [provided by the system after tool execution]\n\n"
    "Repeat Thought/Action/Observation until you have enough information, then write:\n"
    "Final Answer: [your answer]\n\n"
    "Never skip the Thought step. Never act without reasoning first."
)


def demo_react(client) -> None:
    log.info("=" * 60)
    log.info("DEMO 1 — ReAct pattern (Thought → Action → Observation)")
    log.info("=" * 60)
    log.info("Task: %s", RESEARCH_TASK)
    log.info("-" * 60)

    messages = [
        {"role": "system", "content": REACT_SYSTEM},
        {"role": "user", "content": RESEARCH_TASK},
    ]

    # --------------------------------------------------
    # FAILURE CASE
    # --------------------------------------------------
    # Failure case:
    # - Replace REACT_SYSTEM with a plain system prompt (remove the Thought/Action/Observation
    #   format instruction)
    # - Observe:
    #   * The model makes tool calls without producing Thought traces
    #   * The message history has no visible reasoning chain
    #   * Debugging which tool was called for which reason becomes impossible
    #   * This shows why explicit reasoning enforcement is the value of ReAct

    result = run_agent(client, TOOLS, messages, DISPATCHER, max_iterations=MAX_ITERATIONS)

    log.info("-" * 60)
    log.info("FINAL ANSWER: %s", result)
    log.info("")
    log.info(
        "Observe: the model's response content before each tool call should contain "
        "'Thought:' traces. These are visible in the assistant messages in the loop log."
    )


# ---------------------------------------------------------------------------
# Demo 2: Reflection pattern
# ---------------------------------------------------------------------------

# Concept: reflection — post-generation evaluation with revision ceiling
MAX_REVISIONS = 3

REFLECTOR_SYSTEM = (
    "You are a quality evaluator. Given a task and a draft answer, evaluate whether "
    "the answer correctly and completely addresses the task. "
    "Reply with exactly 'APPROVED' if the answer is correct and complete. "
    "Otherwise, list specific issues as bullet points (no more than 3)."
)


def revise(client, task: str, draft: str, issues: str) -> str:
    """Generate a revised answer based on the reflector's issues."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a research assistant. Revise the draft answer to fix "
                    "the listed issues. Keep the answer concise."
                ),
            },
            {
                "role": "user",
                "content": f"Task: {task}\n\nDraft answer:\n{draft}\n\nIssues to fix:\n{issues}",
            },
        ],
    )
    return response.choices[0].message.content or draft


def reflect_and_revise(client, task: str, draft: str, max_revisions: int = MAX_REVISIONS) -> str:
    """
    Reflection loop: evaluate draft, revise on issues, repeat until approved or ceiling.

    Concept: reflection — revision ceiling prevents infinite refinement loops.
    """
    for revision in range(1, max_revisions + 1):
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": REFLECTOR_SYSTEM},
                {
                    "role": "user",
                    "content": f"Task: {task}\n\nAnswer:\n{draft}",
                },
            ],
        )
        evaluation = response.choices[0].message.content or ""

        if "APPROVED" in evaluation.upper():
            log.info("[reflection round %d] APPROVED", revision)
            return draft

        log.info("[reflection round %d] Issues found: %s", revision, evaluation[:120])
        draft = revise(client, task, draft, evaluation)
        log.info("[reflection round %d] Revised answer: %s", revision, draft[:120])

    log.info("[reflection] Revision ceiling reached (%d). Returning last draft.", max_revisions)
    return draft


def demo_reflection(client) -> None:
    log.info("")
    log.info("=" * 60)
    log.info("DEMO 2 — Reflection (evaluate → revise → re-evaluate)")
    log.info("=" * 60)

    task = (
        "Explain in exactly two sentences: what does the ReAct pattern add to a "
        "basic agent loop, and what failure mode does it prevent?"
    )
    log.info("Task: %s", task)
    log.info("-" * 60)

    # Generate initial draft using the basic loop
    messages = [
        {"role": "system", "content": "You are a research assistant. Answer concisely."},
        {"role": "user", "content": task},
    ]
    response = client.chat.completions.create(model=MODEL, messages=messages)
    draft = response.choices[0].message.content or ""
    log.info("Initial draft: %s", draft)
    log.info("-" * 60)

    final = reflect_and_revise(client, task, draft)

    log.info("-" * 60)
    log.info("FINAL ANSWER (after reflection): %s", final)


# ---------------------------------------------------------------------------
# Demo 3: Plan-and-execute pattern
# ---------------------------------------------------------------------------

PLANNER_SYSTEM = (
    "You are a planning agent. Given a research task, produce a numbered execution plan. "
    "Each step should specify: what to do, which tool to use, and what output to expect. "
    "Output ONLY the plan as a numbered list. Do not execute any steps."
)

EXECUTOR_SYSTEM = (
    "You are an execution agent. You follow a given plan step by step using your tools. "
    "After completing each step, report the result before moving to the next step. "
    "If a step fails, report 'STEP FAILED: <reason>' and continue with the remaining steps."
)


def plan(client, task: str) -> str:
    """Planning phase: produce a structured plan without executing any tools."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": PLANNER_SYSTEM},
            {"role": "user", "content": task},
        ],
    )
    return response.choices[0].message.content or ""


def demo_plan_and_execute(client) -> None:
    log.info("")
    log.info("=" * 60)
    log.info("DEMO 3 — Plan-and-execute (plan first, then execute)")
    log.info("=" * 60)

    task = (
        "Research the Transformer architecture: find the key paper, read it, "
        "and extract the main technical contribution and the benchmark result."
    )
    log.info("Task: %s", task)
    log.info("-" * 60)

    # Concept: plan-and-execute — planning phase produces plan without tool calls
    generated_plan = plan(client, task)
    log.info("PLAN:")
    log.info(generated_plan)
    log.info("-" * 60)

    # Execution phase: executor follows the plan using tools
    messages = [
        {"role": "system", "content": EXECUTOR_SYSTEM},
        {
            "role": "user",
            "content": f"Execute this plan:\n\n{generated_plan}\n\nTask: {task}",
        },
    ]

    result = run_agent(client, TOOLS, messages, DISPATCHER, max_iterations=MAX_ITERATIONS)

    log.info("-" * 60)
    log.info("EXECUTION RESULT: %s", result)
    log.info("")
    log.info(
        "Observe: the plan was generated before any tool call. "
        "The executor received the plan as its starting context — "
        "planning and execution were separated into two distinct LLM calls."
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    assert_ollama_ready(models=[MODEL])
    client = build_client()

    demo_react(client)
    demo_reflection(client)
    demo_plan_and_execute(client)
