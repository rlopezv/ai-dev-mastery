# Shared display utilities for frameworks-tools labs
# Doc reference: docs/frameworks-tools/implementation-reference.md


def print_separator(title: str = "", width: int = 60) -> None:
    if title:
        side = (width - len(title) - 2) // 2
        print("=" * side + f" {title} " + "=" * side)
    else:
        print("=" * width)


def print_section(title: str) -> None:
    print(f"\n--- {title} ---")


def print_response(label: str, text: str) -> None:
    print(f"\n[{label}]\n{text}")


def print_sources(docs) -> None:
    """Print source metadata from a list of LangChain Documents."""
    if not docs:
        return
    print("\nSources retrieved:")
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "unknown")
        snippet = doc.page_content[:120].replace("\n", " ")
        print(f"  {i}. {source} — {snippet}...")
