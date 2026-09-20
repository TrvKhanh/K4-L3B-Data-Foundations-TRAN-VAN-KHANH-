from __future__ import annotations

import argparse
from pathlib import Path

DEFAULT_SOURCE_DIR = Path("data/ecommerce")
DEFAULT_OUTPUT = DEFAULT_SOURCE_DIR / "corpus.md"


def merge_markdown_files(source_dir: Path, output_path: Path) -> Path:
    """Merge source Markdown files into one reproducible corpus file."""
    source_files = sorted(
        path for path in source_dir.glob("*.md") if path.name != output_path.name
    )
    if not source_files:
        raise FileNotFoundError(f"No Markdown files found in {source_dir}")

    sections = []
    for path in source_files:
        content = path.read_text(encoding="utf-8").strip()
        sections.append(f"<!-- source: {path.name} -->\n\n{content}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        "# Ecommerce Knowledge Corpus\n\n"
        + "\n\n---\n\n".join(sections)
        + "\n",
        encoding="utf-8",
    )
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    output_path = merge_markdown_files(args.source_dir, args.output)
    print(f"Merged {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
