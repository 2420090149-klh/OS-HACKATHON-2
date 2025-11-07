import json
from pathlib import Path

import pytest

from src import analyzer


def test_analyze_text_happy_path():
    text = "hello world\nthis is a test\n"
    result = analyzer.analyze_text(text)
    assert result["lines"] == 2
    # words: ['hello','world','this','is','a','test'] => 6
    assert result["words"] == 6
    assert result["characters"] == len(text)


def test_analyze_text_empty():
    result = analyzer.analyze_text("")
    assert result["lines"] == 0
    assert result["words"] == 0
    assert result["characters"] == 0


def test_analyze_file_tmp_path(tmp_path: Path):
    p = tmp_path / "sample.txt"
    p.write_text("one two three\nnext line")
    result = analyzer.analyze_file(p)
    # splitlines -> ['one two three','next line'] => 2 lines
    assert result["lines"] == 2
    # words -> ['one','two','three','next','line'] => 5
    assert result["words"] == 5
