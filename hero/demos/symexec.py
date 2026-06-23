# title: Symbolic Execution
# Find the input that gets accepted
import angr
proj = angr.Project("fauxware")
simgr = proj.factory.simgr()

accepted = proj.loader.find_symbol("accepted").rebased_addr
simgr.explore(find=accepted)

simgr.found[0].posix.dumps(0)
