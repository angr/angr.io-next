# A guided angr session on the classic "fauxware" binary.
#
# This is plain angr code — write it the way you'd type it into IPython.
# Blank lines separate "cells" (they become pauses in the playback).
# `hero/play.py` replays this as a typed REPL session and `hero/record_cli.py`
# captures it to src/assets/cli/repl.cast, which the website plays.
#
# Needs angr + the fauxware test binary (set FAUXWARE_DIR=/path if not on PATH).

import angr
proj = angr.Project("fauxware")

# disassemble main
main = proj.loader.find_symbol("main").rebased_addr
proj.factory.block(main).pp()

# recover the control-flow graph
cfg = proj.analyses.CFGFast(normalize=True, show_progressbar=True)
proj.kb.functions["main"]

# decompile main() to C
print(proj.analyses.Decompiler("main").codegen.text)

# symbolically execute to find the backdoor
simgr = proj.factory.simgr()
simgr.explore(find=0x4006ed)   # 'accepted'
simgr.found[0].posix.dumps(0)
