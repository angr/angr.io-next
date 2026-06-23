#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["angr"]
# ///
"""
Replay an IPython-notebook-style Python file as a typed REPL session.

Give it a plain `.py` file (see hero/demos/fauxware.py). Each line is "typed"
at a `>>>` prompt and executed in a persistent namespace, exactly like a REPL —
expression results are echoed, `print()` output appears inline. Blank lines are
treated as cell breaks (a short pause). A leading comment header (before the
first code line) is skipped; inline `# comments` after code begins are shown.

This is what `hero/record_cli.py` runs to produce the REPL tab's asciicast.

    python hero/play.py hero/demos/fauxware.py
"""
import code
import random
import sys
import time

# ---- optional syntax coloring (pygments ships with IPython) ----------------
try:
    from pygments import lex
    from pygments.lexers import PythonLexer
    from pygments.token import Token

    _LEXER = PythonLexer()
    _HAVE_PYGMENTS = True
except Exception:  # pragma: no cover - pygments missing
    _HAVE_PYGMENTS = False

RESET = "\033[0m"
PROMPT_COLOR = "\033[38;5;203m"  # crimson
_TOKEN_COLORS = {
    "Token.Keyword": "\033[38;5;204m",
    "Token.Keyword.Namespace": "\033[38;5;204m",
    "Token.Name.Builtin": "\033[38;5;75m",
    "Token.Name.Function": "\033[38;5;75m",
    "Token.Name.Decorator": "\033[38;5;75m",
    "Token.Literal.String": "\033[38;5;78m",
    "Token.Literal.String.Affix": "\033[38;5;78m",
    "Token.Literal.String.Escape": "\033[38;5;78m",
    "Token.Literal.Number": "\033[38;5;215m",
    "Token.Comment": "\033[38;5;245m",
    "Token.Comment.Single": "\033[38;5;245m",
    "Token.Operator": "\033[38;5;250m",
}

# Timing knobs (seconds).
CHAR_DELAY = 0.011
CHAR_JITTER = 0.014
PROMPT_PAUSE = 0.18
AFTER_STATEMENT = 0.32
CELL_GAP = 0.55


def _color_for(token):
    t = token
    while t is not Token:
        key = str(t)
        if key in _TOKEN_COLORS:
            return _TOKEN_COLORS[key]
        t = t.parent
    return ""


def _w(s):
    sys.stdout.write(s)
    sys.stdout.flush()


def type_line(line):
    """Type a line of code character by character, colored if possible."""
    if _HAVE_PYGMENTS:
        chunks = [(tok, txt) for tok, txt in lex(line, _LEXER)]
    else:
        chunks = [(None, line)]
    for token, text in chunks:
        color = _color_for(token) if token is not None else ""
        if color:
            _w(color)
        for ch in text:
            if ch == "\n":
                continue
            _w(ch)
            time.sleep(CHAR_DELAY + random.random() * CHAR_JITTER)
        if color:
            _w(RESET)
    _w("\n")


def run(path):
    with open(path) as f:
        lines = f.read().splitlines()

    console = code.InteractiveConsole(locals={})
    # Silent prelude: keep library logging out of the recording.
    console.push("import logging as _l; _l.disable(_l.WARNING); del _l")

    started = False  # skip the leading comment header
    more = False
    for raw in lines:
        line = raw.rstrip()
        if not started:
            if line == "" or line.lstrip().startswith("#"):
                continue
            started = True

        if line == "":
            if not more:
                time.sleep(CELL_GAP)
            continue

        # Pause *before* showing the prompt so it never lingers empty — once the
        # prompt appears, typing begins right away, like a real session.
        time.sleep(PROMPT_PAUSE)
        _w(f"{PROMPT_COLOR}{'...' if more else '>>>'}{RESET} ")
        type_line(line)
        more = console.push(line)
        if not more:
            time.sleep(AFTER_STATEMENT)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: play.py <notebook.py>")
    run(sys.argv[1])
