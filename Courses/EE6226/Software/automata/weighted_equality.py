"""
Function to check whether two weighted automata are the same (iso-morph).
Cannot deal with non-deterministic automata.
"""
from automata import algorithm, exceptions

def check_weighted_equality(wa1, wa2):
    """
    Compare deterministic weighted automataton L{wa1} with L{wa2}.

    @param wa1: First automaton to use for comparison.
    @type  wa1: L{WeightedAutomaton}

    @param wa2: Second automaton to use for comparison.
    @type  wa2: L{WeightedAutomaton}

    @return: Automata are equal.
    @rtype:  C{bool}
    """
    def get_edge_dict(state):
        edges = list(state.get_outgoing())
        edict = dict(((edge.label, edge.weight), edge) for edge in edges)
        if len(edges) != len(edict):
            msg = "Non-deterministic weighted automata are not supported " \
                  "by this check."
            raise exceptions.ModelError(msg)
        return edict



    props = algorithm.ManagerProperties(None)
    props.explore_mgr = algorithm.ORIGINAL_STATE

    mgr = algorithm.Manager(props)
    mgr.get_state((wa1.initial, wa2.initial))
    while True:
        sab = mgr.get_next()
        if sab is None:
            break

        sa, sb = sab
        if sa.marked != sb.marked:
            return False

        edges_a = get_edge_dict(sa)
        edges_b = get_edge_dict(sb)
        if len(edges_a) != len(edges_b):
            return False # Different number of outgoing edges => not equal.

        for edge_a in edges_a.itervalues():
            edge_b = edges_b.get((edge_a.label, edge_a.weight))
            if edge_b is None:
                return False

            mgr.get_state((edge_a.succ, edge_b.succ))

    return True
