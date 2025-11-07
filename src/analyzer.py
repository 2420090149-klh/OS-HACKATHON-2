"""Text analyzer with NLP features using NLTK.

Functions:
- analyze_text(text: str) -> dict: returns basic counts (lines, words, chars)
- analyze_text_nlp(text: str) -> dict: returns NLP analysis (tokens, POS tags, etc.)
- analyze_file(path: str) -> dict: reads file and returns both analyses

Provides a CLI to print JSON output for a file or stdin.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Dict, List, Any

# Note: avoid importing heavy NLP libraries at module import time so tests
# and simple usage don't fail if optional dependencies (numpy, nltk wheels)
# are misconfigured on the system. We attempt to import and use NLTK inside
# `analyze_text_nlp` and otherwise fall back to a lightweight implementation.

def analyze_text(text: str) -> Dict[str, int]:
    """Return a basic analysis of the provided text.

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

def analyze_text_nlp(text: str) -> Dict[str, Any]:
    """Return NLP analysis of the text using NLTK.
    
    - sentences: list of sentences
    - tokens: all tokens (words + punctuation)
    - words: tokens without stopwords/punctuation
    - pos_tags: part-of-speech tag frequencies
    - top_words: most common non-stopwords
    """
    if not text:
        return {
            "sentences": 0,
            "tokens": 0,
            "words": 0,
            "pos_tags": {},
            "top_words": []
        }

    # First try to use NLTK if it's importable and working.
    try:
        # import locally to avoid heavy imports at module import time
        from nltk.tokenize import word_tokenize, sent_tokenize
        from nltk.corpus import stopwords as nltk_stopwords
        from nltk.tag import pos_tag as nltk_pos_tag

        # Ensure required data is present (best-effort)
        try:
            import nltk
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt')
            try:
                nltk.data.find('taggers/averaged_perceptron_tagger')
            except LookupError:
                nltk.download('averaged_perceptron_tagger')
            try:
                nltk.data.find('corpora/stopwords')
            except LookupError:
                nltk.download('stopwords')
        except Exception:
            # ignore downloader failures; we'll fall back if something breaks
            pass

        sentences = sent_tokenize(text)
        tokens = word_tokenize(text)
        stops = set(nltk_stopwords.words('english'))
        words = [w.lower() for w in tokens if w.lower() not in stops and w.isalnum()]
        pos_tags = nltk_pos_tag(tokens)
        pos_freq = Counter(tag for _, tag in pos_tags)
        top_words = Counter(words).most_common(5)

        return {
            "sentences": len(sentences),
            "tokens": len(tokens),
            "words": len(words),
            "pos_tags": dict(pos_freq),
            "top_words": top_words
        }
    except Exception:
        # Fallback lightweight implementation (no external deps)
        import re

        # Simple sentence splitter on terminal punctuation
        sentences = [s for s in re.split(r'[.!?]+', text) if s.strip()]
        tokens = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)

        # Minimal stopword set to approximate behavior
        small_stops = {
            'a', 'an', 'the', 'and', 'or', 'but', 'if', 'in', 'on', 'with', 'to',
            'of', 'for', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'this',
            'that', 'these', 'those', 'it', 'as', 'at', 'by', 'from', 'has', 'have', 'had'
        }

        words = [w.lower() for w in tokens if w.isalnum() and w.lower() not in small_stops]

        # Very simple rule-based POS guesser to ensure non-empty pos_tags
        pos_freq = Counter()
        for w in words:
            if w.istitle():
                pos = 'NNP'
            elif w.endswith('ing'):
                pos = 'VBG'
            elif w.endswith('ed'):
                pos = 'VBD'
            elif w in {'is', 'are', 'was', 'be', 'am', 'been', 'being', 'do', 'does', 'did', 'have', 'has', 'had', 'will'}:
                pos = 'VB'
            elif len(w) <= 2:
                pos = 'IN'
            else:
                pos = 'NN'
            pos_freq[pos] += 1

        top_words = Counter(words).most_common(5)

        return {
            "sentences": len(sentences),
            "tokens": len(tokens),
            "words": len(words),
            "pos_tags": dict(pos_freq),
            "top_words": top_words
        }


def analyze_file(path: str | Path) -> Dict[str, int]:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        content = f.read()
    return analyze_text(content)


def analyze_file(path: str | Path) -> Dict[str, Any]:
    """Read file and return both basic and NLP analysis."""
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        content = f.read()
    basic = analyze_text(content)
    nlp = analyze_text_nlp(content)
    return {"basic": basic, "nlp": nlp}


def _main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze a text file with basic counts and NLP features"
    )
    parser.add_argument(
        "--file", "-f", 
        help="Path to file to analyze; if omitted reads stdin", 
        default=None
    )
    parser.add_argument(
        "--format", 
        choices=["pretty", "json"], 
        default="pretty",
        help="Output format (pretty=formatted, json=raw JSON)"
    )
    args = parser.parse_args()
    
    if args.file:
        result = analyze_file(args.file)
    else:
        import sys
        content = sys.stdin.read()
        basic = analyze_text(content)
        nlp = analyze_text_nlp(content)
        result = {"basic": basic, "nlp": nlp}
    
    if args.format == "pretty":
        print("\nBasic Analysis:")
        print("-" * 40)
        for k, v in result["basic"].items():
            print(f"{k:12}: {v}")
        
        print("\nNLP Analysis:")
        print("-" * 40)
        nlp = result["nlp"]
        print(f"{'sentences':12}: {nlp['sentences']}")
        print(f"{'tokens':12}: {nlp['tokens']}")
        print(f"{'words':12}: {nlp['words']} (excluding stopwords)")
        
        print("\nPart-of-Speech Tags:")
        for tag, count in nlp["pos_tags"].items():
            print(f"{tag:12}: {count}")
        
        print("\nTop 5 Words:")
        for word, count in nlp["top_words"]:
            print(f"{word:12}: {count}")
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    _main()
