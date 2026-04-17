# Lab: lab-semantic-kernel
# Module: frameworks-tools
# Doc reference: docs/frameworks-tools/semantic-kernel.md

import sys
import asyncio
import pathlib
import logging

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from shared.config import OPENAI_API_KEY, OPENAI_MODEL, assert_openai_key
from shared.utils import print_separator, print_section, print_response

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import (
    OpenAIChatCompletion,
    OpenAIChatPromptExecutionSettings,
)
from semantic_kernel.functions import kernel_function

logging.basicConfig(level=logging.WARNING)

# ---------------------------------------------------------------------------
# Plugin definitions
# ---------------------------------------------------------------------------

class MathPlugin:
    """Native functions for mathematical operations."""

    # Concept: native function — @kernel_function exposes a Python method to the kernel
    @kernel_function(
        name="multiply",
        description="Multiplies two numbers and returns the result as a string.",
    )
    def multiply(self, a: float, b: float) -> str:
        result = a * b
        return f"{a} × {b} = {result}"

    @kernel_function(
        name="square_root",
        description="Returns the square root of a number as a string.",
    )
    def square_root(self, n: float) -> str:
        import math
        result = math.sqrt(n)
        return f"√{n} = {result:.4f}"


class DocumentPlugin:
    """Semantic functions for document processing."""

    def __init__(self, kernel: Kernel):
        self._kernel = kernel

    # Concept: semantic function — inline prompt template registered as a kernel function
    @kernel_function(
        name="summarize",
        description=(
            "Summarizes the provided technical text into exactly three bullet points. "
            "Each bullet starts with a dash and a key concept name in bold."
        ),
    )
    async def summarize(self, text: str) -> str:
        result = await self._kernel.invoke_prompt(
            "Summarize this technical text into exactly three bullet points. "
            "Each bullet must start with a dash and a bold concept name.\n\nText:\n{{$text}}",
            text=text,
        )
        return str(result)

    @kernel_function(
        name="format_report",
        description=(
            "Formats a bullet-point summary into a professional technical report "
            "with a title, introduction sentence, and numbered findings."
        ),
    )
    async def format_report(self, summary: str, topic: str) -> str:
        result = await self._kernel.invoke_prompt(
            "Format this summary into a professional technical report with a title "
            "for '{{$topic}}', an introduction sentence, and numbered findings.\n\n"
            "Summary:\n{{$summary}}",
            summary=summary,
            topic=topic,
        )
        return str(result)


# ---------------------------------------------------------------------------
# Build kernel
# ---------------------------------------------------------------------------

def build_kernel() -> Kernel:
    kernel = Kernel()
    # Concept: kernel — central registry that holds AI services and plugins
    kernel.add_service(
        OpenAIChatCompletion(
            service_id="default",
            ai_model_id=OPENAI_MODEL,
            api_key=OPENAI_API_KEY,
        )
    )
    return kernel


# ---------------------------------------------------------------------------
# Demo 1: direct plugin function invocation
# ---------------------------------------------------------------------------

async def demo_direct_invocation(kernel: Kernel) -> None:
    print_separator("DEMO 1 — Direct plugin function invocation")

    # Concept: plugin — named collection of native and semantic functions
    math_plugin = kernel.add_plugin(MathPlugin(), plugin_name="Math")
    doc_plugin = kernel.add_plugin(DocumentPlugin(kernel), plugin_name="Documents")

    print_section("Native function: Math.multiply")
    result = await kernel.invoke(math_plugin["multiply"], a=42.0, b=17.0)
    print(f"  Result: {result}")

    print_section("Native function: Math.square_root")
    result = await kernel.invoke(math_plugin["square_root"], n=714.0)
    print(f"  Result: {result}")

    sample_text = (
        "HNSW builds a multi-layer navigable graph for approximate nearest-neighbor "
        "search. Queries traverse from the top coarse layer down to finer layers, "
        "greedy-walking toward the target vector. Parameters M and ef_search control "
        "the recall-latency trade-off without rebuilding the index."
    )

    print_section("Semantic function: Documents.summarize")
    result = await kernel.invoke(doc_plugin["summarize"], text=sample_text)
    print_response("Summary", str(result))


# ---------------------------------------------------------------------------
# Demo 2: planner selects functions based on task description
# ---------------------------------------------------------------------------

async def demo_planner(kernel: Kernel) -> None:
    print_separator("DEMO 2 — Planner selects plugin functions")

    # Concept: planner — FunctionChoiceBehavior presents all functions to the LLM as tools
    settings = OpenAIChatPromptExecutionSettings(
        function_choice_behavior="auto",
        max_tokens=1024,
    )

    task = (
        "Summarize the following technical text and then format the summary into a "
        "professional report on the topic 'Vector Search'. "
        "Text: HNSW (Hierarchical Navigable Small World) builds a multi-layer graph "
        "for approximate nearest-neighbor search. Queries traverse from the top layer "
        "down, greedy-walking toward the target vector. Parameters M and ef_search "
        "control recall and latency trade-offs."
    )

    print(f"Task: {task[:120]}...\n")
    print("Planner execution (verbose):")

    result = await kernel.invoke_prompt(task, settings=settings)
    print_response("Final output", str(result))

    # --------------------------------------------------
    # FAILURE CASE
    # --------------------------------------------------
    # Failure case:
    # - Change the description of Documents.summarize in DocumentPlugin to:
    #   description="Processes text."
    # - Re-run Demo 2
    # - Observe:
    #   * The planner does not select Documents.summarize for a summarization task
    #   * It may skip to Documents.format_report directly or answer without using plugins
    #   * The final output lacks bullet-point structure because the summarize step was skipped
    #   * This demonstrates that function descriptions are the planner's selection signal


# ---------------------------------------------------------------------------
# Demo 3: chained function invocation (explicit, no planner)
# ---------------------------------------------------------------------------

async def demo_chained(kernel: Kernel) -> None:
    print_separator("DEMO 3 — Explicit chained invocation")
    print("Calls summarize → format_report explicitly, without planner.\n")

    doc_plugin = kernel.plugins["Documents"]

    text = (
        "Multi-agent coordination patterns include orchestrator-subagent, where a "
        "coordinator decomposes tasks and delegates to specialized subagents with "
        "isolated context. The GroupChat model uses a shared transcript; the "
        "isolated-state model keeps each agent's accumulator separate. Context "
        "isolation is critical to prevent token cost from growing O(n × agents)."
    )

    print_section("Step 1: Documents.summarize")
    summary_result = await kernel.invoke(doc_plugin["summarize"], text=text)
    summary = str(summary_result)
    print(summary)

    print_section("Step 2: Documents.format_report")
    report_result = await kernel.invoke(
        doc_plugin["format_report"], summary=summary, topic="Multi-Agent Coordination"
    )
    print_response("Final report", str(report_result))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main() -> None:
    kernel = build_kernel()

    await demo_direct_invocation(kernel)
    await demo_planner(kernel)
    await demo_chained(kernel)


if __name__ == "__main__":
    assert_openai_key()
    asyncio.run(main())
