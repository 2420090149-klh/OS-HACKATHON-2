# OS-HACKATHON-2

This repository was empty — I added a small Python text analyzer scaffold with tests.

Files added:
- `src/analyzer.py` — library + CLI (analyze text or file; prints JSON)
- `tests/test_analyzer.py` — pytest unit tests (happy path + edge cases)
- `requirements.txt` — lists `pytest` for running tests

Quick start (Windows PowerShell):

```powershell
# create and activate virtual env (optional but recommended)
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# run tests
python -m pytest -q
# run analyzer on a file
python -m src.analyzer --file README.md
```

Let me know if you want a different feature set for the analyzer or CI added.