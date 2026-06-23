#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["angr"]
# ///
"""
Record real angr command-line sessions to asciicasts for the website's CLI
section. Each demo "types" a command, then runs the real `python -m angr ...`
under a pseudo-terminal and captures its colored output verbatim.

    python hero/record_cli.py      # -> src/assets/cli/*.cast + manifest.json

Needs angr + the fauxware test binary (override the dir with FAUXWARE_DIR).
Add or edit entries in DEMOS to change which commands are showcased; each
becomes a tab in the CLI section. Commit the regenerated casts + manifest.
"""
import fcntl
import json
import os
import pty
import select
import struct
import sys
import termios
import time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.normpath(os.path.join(HERE, "..", "src", "assets", "cli"))
BIN_DIR = os.environ.get(
    "FAUXWARE_DIR",
    os.path.normpath(os.path.join(HERE, "..", "..", "binaries", "tests", "x86_64")),
)

COLS, ROWS = 110, 26
MAX_IDLE = 1.0  # clamp the analysis pause so playback stays snappy
HOLD = 5.0  # seconds to rest on the final output before the loop restarts
PROMPT = "\x1b[38;5;203m$\x1b[0m "  # crimson `$`
CHAR_DELAY = 0.025

_PY = sys.executable
# Wrapper that keeps unicode CFG edges even while progress bars are on.
_WRAP = os.path.join(HERE, "_angr_cli.py")
_PLAY = os.path.join(HERE, "play.py")
_FAUXWARE_NB = os.path.join(HERE, "demos", "fauxware.py")
_FUNCS = ["main", "authenticate", "rejected", "accepted"]

# Each tab is a real recording. kind "command" types a `$ ...` prompt then runs
# the angr CLI; kind "repl" records a typed Python REPL session (play.py) as-is.
DEMOS = [
    {
        "id": "decompile",
        "title": "Decompile",
        "display": "angr decompile fauxware --functions " + " ".join(_FUNCS),
        "argv": [_PY, _WRAP, "decompile", "fauxware", "--functions", *_FUNCS],
    },
    {
        "id": "disassemble",
        "title": "Disassemble",
        "display": "angr disassemble fauxware --functions " + " ".join(_FUNCS),
        "argv": [_PY, _WRAP, "disassemble", "fauxware", "--functions", *_FUNCS],
    },
    {
        "id": "repl",
        "title": "Python REPL",
        "kind": "repl",
        "argv": [_PY, _PLAY, _FAUXWARE_NB],
    },
]


def type_events(display):
    """asciicast events that type the prompt + command, char by char."""
    events = [[0.0, "o", PROMPT]]
    t = 0.3
    for ch in display:
        events.append([round(t, 4), "o", ch])
        t += CHAR_DELAY
    t += 0.4
    events.append([round(t, 4), "o", "\r\n"])
    return events, t


def record_cmd(argv, start):
    """Run argv under a pty; return output events offset to begin at `start`."""
    env = dict(
        os.environ,
        TERM="xterm-256color",
        COLUMNS=str(COLS),
        LINES=str(ROWS),
        PYTHONUNBUFFERED="1",
        FORCE_COLOR="1",
        # angr draws unicode control-flow edges only when stdout.encoding is
        # exactly "utf-8"; force it so we don't fall back to ASCII edges.
        PYTHONIOENCODING="utf-8",
    )
    events = []
    pid, fd = pty.fork()
    if pid == 0:  # child
        os.execvpe(argv[0], argv, env)
        os._exit(127)

    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", ROWS, COLS, 0, 0))
    t0 = time.time()
    last = t0
    while True:
        try:
            r, _, _ = select.select([fd], [], [], 3)
        except (InterruptedError, OSError):
            break
        if fd not in r:
            continue
        try:
            data = os.read(fd, 65536)
        except OSError:
            break
        if not data:
            break
        now = time.time()
        if now - last > MAX_IDLE:
            t0 += (now - last) - MAX_IDLE
        last = now
        events.append([round(start + (now - t0), 4), "o",
                       data.decode("utf-8", "replace")])
    os.close(fd)
    status = 0
    try:
        _, status = os.waitpid(pid, 0)
    except OSError:
        pass
    # Fail loudly instead of baking an error message into the cast — this is what
    # makes `gen:cli` a real validation gate when a demo breaks against angr.
    code = os.waitstatus_to_exitcode(status)
    if code != 0:
        raise SystemExit(f"command exited with {code}: {' '.join(argv)}")
    return events


def record_demo(demo):
    if demo.get("kind") == "repl":
        # play.py types its own prompts, so record it raw (no `$ ...` prefix).
        events = record_cmd(demo["argv"], 0.3)
    else:
        typed, t = type_events(demo["display"])
        events = typed + record_cmd(demo["argv"], t + 0.3)
    # Rest on the final output for a while before the player loops back, so the
    # result is actually readable instead of flashing past.
    if events:
        events.append([round(events[-1][0] + HOLD, 4), "o", "\x1b[0m"])
    header = {
        "version": 2,
        "width": COLS,
        "height": ROWS,
        "env": {"TERM": "xterm-256color"},
        "title": f"angr {demo['id']}",
    }
    path = os.path.join(OUT_DIR, demo["id"] + ".cast")
    with open(path, "w") as f:
        f.write(json.dumps(header) + "\n")
        for ev in events:
            f.write(json.dumps(ev) + "\n")
    dur = events[-1][0] if events else 0
    print(f"  {demo['id']}.cast  ({len(events)} events, {dur:.1f}s)")
    return {"id": demo["id"], "title": demo["title"]}


def _up_to_date(output, *sources):
    """True if `output` exists and is at least as new as every source file."""
    try:
        out_mtime = os.path.getmtime(output)
    except OSError:
        return False
    return all(os.path.getmtime(s) <= out_mtime for s in sources)


def main():
    # Skip re-recording if the casts are newer than this script, the CLI wrapper,
    # play.py, and the REPL demo — like `make`. Pass --force to rebuild anyway.
    out = os.path.join(OUT_DIR, "manifest.json")
    sources = [os.path.abspath(__file__), _WRAP, _PLAY, _FAUXWARE_NB]
    if "--force" not in sys.argv and _up_to_date(out, *sources):
        print("CLI casts are up to date — skipping (--force to rebuild)")
        return
    os.makedirs(OUT_DIR, exist_ok=True)
    if os.path.isdir(BIN_DIR):
        os.chdir(BIN_DIR)
    manifest = [record_demo(d) for d in DEMOS]
    with open(os.path.join(OUT_DIR, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")
    print(f"wrote {OUT_DIR}/manifest.json ({len(manifest)} demos)")


if __name__ == "__main__":
    main()
