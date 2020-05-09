#
# $Id: common.py 587 2010-01-14 13:34:04Z hat $
#
"""
Commonly used unctions
"""
import os, sys, time, re

# Check whether we have access to memory usage information.
if sys.platform.startswith('linux'):
    # Assume linux platform
    memsize_available = os.path.isfile('/proc/self/status')
    vmsize_pat = re.compile('VmSize:\\s+(\\d+\\s+kB)\\s+$')
else:
    # Assuming windows system
    memsize_available = False
    vmsize_pat = None
    try:
        import win32process
        memsize_available = True
    except ImportError:
        memsize_available = False


def get_prod_state(orig_state, is_marked, new_aut, state_map, notdone_list):
    """
    Local function to convert a an original state to a state in
    the new automaton.
    The L{state_map} keeps the mapping, pairs of (orig_state, new state). When
    a new state is created, the tuple is also appended to the L{notdone_list}
    to enable iterative exploration of new states.

    @param orig_state: Some form of combined state of the original automaton
    @type  orig_state: Hashable data structure over L{State}

    @param is_marked: Boolean indicating the new state should be a marker state
    @type  is_marked: C{bool}

    @param new_aut: New automaton
    @type  new_aut: L{Automaton}

    @param state_map: Mapping of original state representation to states in the
                      new automaton
    @type  state_map: C{dict} of L{orig_state} to L{State}

    @param notdone_list: List of unexplored states
    @type  notdone_list: C{list} of C{tuple} (L{orig_state}, L{State})

    @return: State representing the L{orig_state} in the new automaton
    @rtype: L{State}

    @todo: Make me obsolete.
    """
    new_state = state_map.get(orig_state, None)
    if new_state is None:
        new_state = new_aut.add_new_state(marked = is_marked)
        state_map[orig_state] = new_state
        notdone_list.append((orig_state, new_state))

    return new_state


def print_line(lines):
    """
    Print L{lines} to the terminal, adding an indication of the time and the
    amount of used memory.

    @param lines: Line(s) of text to print.
    @type  lines: C{str}
    """
    now = time.asctime(time.localtime())

    # Get memory use
    if not memsize_available:
        # No information available
        mem_size = "unknown"
    elif sys.platform.startswith('linux'):
        # Linux platform
        mem_size = linux_memusage()
    else:
        # Windows platform
        mem_size = xp_memusage()

    lines = [line.strip() for line in lines.split('\n')]
    if memsize_available:
        print "%s: %s\t(memory=%s)" % (now, lines[0], mem_size)
    else:
        print "%s: %s" % (now, lines[0])

    if len(lines) > 1:
        indent = " " * (len(now) + 2)
        for line in lines[1:]:
            print "%s%s" % (indent, line)


def xp_memusage():
    """ Retrieve memory usage for own process at Win32 platform. """
    global memsize_available

    assert memsize_available
    current_process = win32process.GetCurrentProcess()
    memory_info = win32process.GetProcessMemoryInfo(current_process)
    return "%d bytes" % memory_info["WorkingSetSize"]

def linux_memusage():
    """ Retrieve memory usage for own process at Linux platform. """
    global memsize_available, vmsize_pat

    assert memsize_available
    mem_size = "??? kB"
    data = open('/proc/self/status','r').readlines()
    for dat in data:
        mo = vmsize_pat.match(dat)
        if mo:
            mem_size = mo.group(1)
            break
    return mem_size

