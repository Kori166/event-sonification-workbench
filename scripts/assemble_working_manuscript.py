"""Assemble the repository dissertation working manuscript in canonical chapter order."""

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "docs" / "dissertation" / "chapters"
OUTPUT = ROOT / "docs" / "dissertation" / "working-manuscript.md"

ORDER = (
    "00-abstract.md",
    "01-introduction.md",
    "02-literature-review.md",
    "03-methodology-and-research-design.md",
    "04-workbench-design-and-implementation.md",
    "05-technical-evaluation-and-results.md",
    "06-discussion.md",
    "07-ethical-considerations-and-critical-reflection.md",
    "08-conclusion-and-future-work.md",
    "09-references.md",
)

HEADER = """# Dissertation working manuscript

> This is the repository working manuscript for whole-document review, citation audit and
> evidence audit. It is not the final formatted assessment artefact. The authoritative submission
> remains the dissertation transferred to and formatted in Word/PDF after editorial compression,
> layout checking, proofreading and supervisor review.

**Working title:** *A Reproducible Workbench for Event-Based Sonification of Annotated Video Datasets*

---
"""


def main() -> None:
    sections = [HEADER.rstrip()]
    for name in ORDER:
        path = CHAPTERS / name
        text = path.read_text(encoding="utf-8").strip()

        def rebase_link(match: re.Match[str]) -> str:
            target = match.group("target")
            if "://" in target or target.startswith(("#", "mailto:")):
                return match.group(0)
            path_part, marker, fragment = target.partition("#")
            resolved = (CHAPTERS / path_part).resolve()
            rebased = os.path.relpath(resolved, OUTPUT.parent).replace(os.sep, "/")
            suffix = f"#{fragment}" if marker else ""
            return f'{match.group("prefix")}{rebased}{suffix})'

        text = re.sub(
            r'(?P<prefix>!?\[[^\]]*\]\()(?P<target>[^)]+)\)',
            rebase_link,
            text,
        )
        sections.append(text)
    OUTPUT.write_text("\n\n---\n\n".join(sections) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
