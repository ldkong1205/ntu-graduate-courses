#
# $Id: path.py 620 2010-01-25 13:54:15Z hat $
#
"""
Path and string functions
"""
from automata import baseobjects, exceptions

class Path(baseobjects.BaseObject):
    """
    Path in the graph, each L{Path} extends a previous path by one step to allow
    sharing of paths. The initial path has not L{prev} path.

    @ivar node: Node of this path.
    @type node: An object expressing position

    @ivar cost: Cost to get here.
    @type cost: An object expressing cost

    @ivar prev: Previous path if it exists.
    @type prev: L{Path} or C{None}

    @ivar evt: Event used to get here if it exists.
    @type evt: Object expressing the event or C{None}
    """
    def __init__(self, node, cost, prev, evt):
        self.node = node
        self.cost = cost
        self.prev = prev
        self.evt  = evt

    def __str__(self):
        return "Path: node = %r, cost = %s" % (self.node, self.cost)


def get_path_list(path):
    """
    Expand the path to a sequence of nodes and costs.

    @param path: Path to return in text form.
    @type  path: L{Path}

    @return: Sequence of nodes and steps from start to finish.
    @rtype:  C{list} of (L{BaseState}, max+ cost-vector, evt-to-next)
    """
    # Build the path from end back to beginning.
    nodes = []
    prevevt = None
    while path is not None:
        nodes.append((path.node, path.cost, prevevt))
        prevevt = path.evt
        path = path.prev

    nodes.reverse()
    return nodes


def find_border_crossing(subset, path, final_state):
    """
    Find the transition that steps outside the safe L{subset}.

    @param subset: Set of states that are safe.
    @type  subset: C{set} of L{State}

    @param path: Path from starting state to L{final_state}, sequence of state
                 and its outgoing edge.
    @type  path: C{list} of pairs (L{State}, L{Event}

    @param final_state: Final state of the path.
    @type  final_state: L{State}

    @return: C{None} if the path stays within the safe subset, else a triplet
             (from-state, event, dest-state).
    @rtype:  Either C{None} or (L{State}, L{Event}, L{State})

    @precond: Initial state of the path must be in L{subset}
    """
    if len(path) == 0:
        # No path => final_state is also the first state => must be safe
        assert final_state in subset
        return None

    assert path[0][0] in subset

    pred_state, pred_evt = None, None
    for state, evt in path:
        if pred_state is not None and state not in subset:
            # Tests may hold for the second or further entry of the path
            return (pred_state, pred_evt, state)

        pred_state, pred_evt = state, evt

    if final_state in subset:
        return None

    return (pred_state, pred_evt, final_state)



def has_string(state, evtseq, state_func = None):
    """
    From L{state}, can a path be found for the string L{evtseq}?

    @param state: Starting state.
    @type  state: L{State}

    @param evtseq: Event sequence describing the string to be found.
    @type  evtseq: C{list} of L{Event}

    @param state_func: Custom function for deciding whether a reached final
                       state is a valid solution.
    @type  state_func: If C{None} all found states are valid. Otherwise, the
                       function is called with a found end-state. It should
                       return a boolean whether the state is acceptable.

    @return: Boolean indicating the string exists
    @rtype:  C{bool}
    """
    if len(evtseq) == 0:
        if state_func is None:
            return True
        return state_func(state)

    for edge in state.get_outgoing(evtseq[0]):
        if has_string(edge.succ, evtseq[1:]):
            return True
    return False


def get_path(start_state, dest_state):
    """
    Compute a path from L{start_state} to L{dest_state}.

    @param start_state: Starting state of the path.
    @type  start_state: L{State}

    @param dest_state: End state of the path.
    @type  dest_state: L{State}

    @return: C{None} if path cannot be found, or a sequence of
             (state, outgoing event) pairs that leads from the initial
             state to the given state.
    @rtype:  C{None} or a C{list} of (L{State}, L{Event})

    @note: L{dest_state} is not in the returned path.
    """

    # 1. Compute minimal distances from end state while going backwards
    #    Distance increases as we move away from dest_state
    distances = {dest_state: 0}
    next_distance = 1
    last_added = [dest_state]

    while start_state not in distances:
        # Crawl back one more step
        if len(last_added) == 0:
            return None

        new_added = []
        for state in last_added:
            for edge in state.get_incoming():
                if edge.pred not in distances:
                    distances[edge.pred] = next_distance
                    new_added.append(edge.pred)

        next_distance = next_distance + 1
        last_added = new_added
        new_added = []  # Clean up, not really necessary

    # Here, start_state has a known distance to dest_state

    # 2. From the start_state, step towards the dest_state
    #    guided by the distances
    path = []
    while start_state != dest_state:
        next_distance = distances[start_state] - 1 # Distance we are looking for
        foundit = False
        for edge in start_state.get_outgoing():
            if edge.succ in distances and distances[edge.succ] == next_distance:
                path.append((start_state, edge.label))
                start_state = edge.succ
                foundit = True
                break

        assert foundit

    distances.clear() # Clean up, not really needed
    return path


def convert_string_to_event_sequence(path_text, alphabet):
    """
    Convert a textual path (a sequence of event names, comma or white-space
    seperated) to a sequence of L{Event}.

    @param path_text: Text forming the path.
    @type  path_text: C{str}

    @param alphabet: Alphabet with events available for use.
    @type  alphabet: C{set} of L{Event}

    @return: Path of events.
    @rtype:  C{list} of L{Event}
    """
    evt_map = dict((evt.name, evt) for evt in alphabet)
    path_text = path_text.replace(',', ' ')

    evt_path = []
    for txt in path_text.split():
        evt = evt_map.get(txt)
        if evt is None:
            msg = "Cannot construct path %r, event %s is not in the alphabet." \
                    % (path_text, txt)
            raise exceptions.InputError(msg)

        evt_path.append(evt)

    return evt_path

