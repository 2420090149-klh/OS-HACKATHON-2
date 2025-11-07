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


def test_analyze_text_nlp():
    text = "The quick brown fox jumps over the lazy dog. This is a test sentence!"
    result = analyzer.analyze_text_nlp(text)
    
    assert result["sentences"] == 2  # Two sentences
    assert result["tokens"] > result["words"]  # More tokens than words (includes punctuation)
    assert all(isinstance(count, int) for count in result["pos_tags"].values())
    assert len(result["top_words"]) <= 5  # Up to 5 top words
    
    # Common words should exclude stopwords like "the" and "is"
    common_words = [word for word, _ in result["top_words"]]
    assert not any(w in ["the", "is", "a"] for w in common_words)


def test_analyze_text_nlp_empty():
    result = analyzer.analyze_text_nlp("")
    assert result["sentences"] == 0
    assert result["tokens"] == 0
    assert result["words"] == 0
    assert result["pos_tags"] == {}
    assert result["top_words"] == []


def test_analyze_file_tmp_path(tmp_path: Path):
    p = tmp_path / "sample.txt"
    p.write_text("The quick brown fox jumps. Another line here.")
    result = analyzer.analyze_file(p)
    
    # Check basic analysis
    assert result["basic"]["lines"] == 1
    assert result["basic"]["words"] == 8
    
    # Check NLP analysis
    assert result["nlp"]["sentences"] == 2
    assert result["nlp"]["tokens"] >= result["basic"]["words"]  # Should have punctuation tokens
    assert len(result["nlp"]["pos_tags"]) > 0
    assert isinstance(result["nlp"]["top_words"], list)
