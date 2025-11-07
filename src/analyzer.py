"""Simple text analyzer CLI and library.

Functions:
- analyze_text(text: str) -> dict: returns counts for lines, words, characters
- analyze_file(path: str) -> dict: reads file and returns analyze_text result

Provides a tiny CLI to print JSON output for a file or stdin.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict


def analyze_text(text: str) -> Dict[str, int]:
    """Return a small analysis of the provided text.

    - lines: number of logical lines (using str.splitlines())
    - words: number of whitespace-separated tokens
    - characters: number of characters in the string
    """
    if text is None:
        text = ""
    lines = text.splitlines()
    num_lines = len(lines)
    # split on any whitespace
    words = text.split()
    num_words = len(words)
    num_chars = len(text)
    return {"lines": num_lines, "words": num_words, "characters": num_chars}


def analyze_file(path: str | Path) -> Dict[str, int]:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        content = f.read()
    return analyze_text(content)


def _main() -> None:
    parser = argparse.ArgumentParser(description="Analyze a text file (lines/words/characters)")
    parser.add_argument("--file", "-f", help="Path to file to analyze; if omitted reads stdin", default=None)
    args = parser.parse_args()
    if args.file:
        result = analyze_file(args.file)
    else:
        import sys

        content = sys.stdin.read()
        result = analyze_text(content)
    print(json.dumps(result))


if __name__ == "__main__":
    _main()
