#
# $Id: weighted_supervisor.py 726 2010-04-08 10:40:22Z hat $
#
"""
Helper functions for constructing weighted supervisors.
"""
from automata import algorithm, supervisor, compute_weight, common, \
                     weighted_projection, weighted_product, conversion, \
                     product, maxplus

# {{{ weighted_determinization(waut):
def weighted_determinization(waut):
    """
    Make equivalent deterministic unweighted automaton.

    @param waut: Input automaton.
    @type  waut: L{WeightedAutomaton}

    @return: Deterministic weighted automaton.
    @rtype:  L{WeightedAutomaton}
    """
    props = algorithm.ManagerProperties(waut.collection)
    props.alphabet = waut.alphabet
    props.aut_type = algorithm.WEIGHTED_AUT
    props.marker_func = algorithm.MARKED_ANY
    props.edge_calc = algorithm.MAX_WEIGHT_EDGE
    props.explore_mgr = algorithm.ORIGINAL_STATE

    return supervisor.common_determinization(waut.initial, props)

# }}} def weighted_determinization(waut):

# {{{ def compute_weighted_supervisor(comp, req):
def compute_weighted_supervisor(comp, req):
    """
    Compute weighted supervisor.

    @param comp: Available component (weighted automaton).
    @type  comp: C{WeightedAutomaton}

    @param req: Available requirement (unweighted automaton).
    @type  req: C{UnweightedAutomaton}

    @return: Resulting supervisor (unweighted automaton).
    @type:   C{UnweightedAutomaton}

    @note: It starts the same way as L{compute_optimal_weighted_supervisor}.
    """
    # Compute supremal supervisor without considering weight.
    wsup = compute_weight.compute_weighted_supremal(comp, req)
    if wsup is None:
        return None

    obs_alphabet = set(evt for evt in comp.alphabet if evt.observable)
    waut2 = weighted_projection.weighted_projection(wsup, obs_alphabet)
    waut2 = weighted_determinization(waut2)
    weight_map = compute_weight.compute_state_weights(waut2,
                                                    marker_valfn = lambda s: 0)

    props = algorithm.ManagerProperties(waut2.collection)
    props.aut_type = algorithm.UNWEIGHTED_AUT
    props.alphabet = waut2.alphabet
    props.marker_func = algorithm.MARKED_ANY
    props.explore_mgr = algorithm.ORIGINAL_STATE
    props.edge_calc = algorithm.COPY_LABEL

    mgr = algorithm.Manager(props)

    mgr.set_initial((waut2.initial,))
    while True:
        state = mgr.get_next()
        if state is None:
            break

        state = state[0]
        for edge in state.get_outgoing():
            dest_weight = maxplus.otimes(weight_map[edge.succ], edge.weight)
            if maxplus.equal(weight_map[state], dest_weight) or \
                    maxplus.biggerthan(weight_map[state], dest_weight):
                mgr.add_edge((edge.pred,), (edge.succ,), [edge])

    unw_comp = conversion.remove_weights(comp)
    result = product.n_ary_unweighted_product([unw_comp, mgr.get_automaton()])

    return result

# }}}
# {{{ def compute_optimal_weighted_supervisor(comp, req):
def compute_optimal_weighted_supervisor(comp, req):
    """
    Compute optimal weighted supervisor.

    @param comp: Available component (weighted automaton).
    @type  comp: C{WeightedAutomaton}

    @param req: Available requirement (unweighted automaton).
    @type  req: C{UnweightedAutomaton}

    @return: Resulting supervisor (unweighted automaton).
    @type:   C{UnweightedAutomaton}
    """
    # Compute supremal supervisor without considering weight.
    wsup = compute_weight.compute_weighted_supremal(comp, req)
    if wsup is None:
        return None

    obs_alphabet = set(evt for evt in comp.alphabet if evt.observable)
    waut2 = weighted_projection.weighted_projection(wsup, obs_alphabet)
    waut2 = weighted_determinization(waut2)
    weight_map = compute_weight.compute_state_weights(waut2,
                                                    marker_valfn = lambda s: 0)
    # Throw out all states with infinite weight.
    waut3 = remove_automaton_states(waut2,
                               lambda s: weight_map[s] is not maxplus.INFINITE)
    waut3.reduce(True, False)

    reduced_comp = weighted_product.n_ary_weighted_product([comp, waut3],
                                                          algorithm.FIRST_EDGE)

    unfolded, weight_map = compute_weight.unfold_automaton_map(reduced_comp,
                                               weight_map[waut2.initial])


    comp = conversion.remove_weights(comp)
    sup = unfolded
    prev_unfolded = None
    while True:
        sup = supervisor.make_supervisor([comp], [sup])
        if sup is None:
            break

        prev_unfolded = sup # 'sup' is a good solution.

        sup = sup.copy()
        state_map = make_state_mapping(sup, unfolded)
        max_weight = max(weight_map[state_map[state]]
                         for state in sup.get_states()
                         if sum(1 for edge in state.get_outgoing()) == 0)

        common.print_line("Pruning weight %d" % max_weight)
        for state in list(sup.get_states()):
            if weight_map[state_map[state]] == max_weight and \
                    sum(1 for edge in state.get_outgoing()) == 0:
                sup.remove_state(state)

    assert prev_unfolded is not None
    return prev_unfolded
# }}}

# {{{ def make_state_mapping(orig_aut, new_aut):
def make_state_mapping(orig_aut, new_aut):
    """
    Construct a map from states in L{orig_aut} to states in L{new_aut}.

    @param orig_aut: Original automaton.
    @type  orig_aut: L{Automaton}

    @param new_aut: New automaton.
    @type  new_aut: L{Automaton}

    @return: Mapping of old states to new states.
    @rtype:  C{dict} of L{State} to L{State}

    @todo: Edgemap seems a generic method on a state.
    """
    mapping = {new_aut.initial : orig_aut.initial}
    not_done = [(new_aut.initial, orig_aut.initial)]
    while len(not_done) > 0:
        new_state, orig_state = not_done.pop()

        # Construct mapping of outgoing edges.
        new_edges = {} #: Mapping of edge properties to dest-state.
        for new_edge in new_state.get_outgoing():
            assert new_edge.label not in new_edges
            new_edges[new_edge.label] = new_edge.succ

        # From new automaton, find matching edges, and update the states to
        # explore.
        for orig_edge in orig_state.get_outgoing():
            not_done.append((new_edges[orig_edge.label], orig_edge.succ))
            mapping[orig_edge.succ] = new_edges[orig_edge.label]
            del new_edges[orig_edge.label] # To prevent a second use.

    return mapping

# }}}
# {{{ def remove_automaton_states(waut, pred_fn):
def remove_automaton_states(waut, pred_fn):
    """
    Make a copy of L{waut}, with states removed for which L{pred_fn} does not
    hold.

    @param waut: Input automaton.
    @type  waut: L{WeightedAutomaton}

    @param pred_fn: Predicate function.
    @type  pred_fn: C{func} from L{WeightedState} to C{bool}

    @return: Resulting automaton.
    @rtype:  L{WeightedAutomaton}
    """
    res_waut = waut.copy()

    for state in waut.get_states():
        if not pred_fn(state):
            res_waut.remove_state(res_waut.get_state(state.number))

    return res_waut
# }}}


def reduce_automaton(waut, wvalues, evtdata, num_res, start = None):
    """
    Reduce the weighted automaton.

    @param waut: (Weighted) automaton (the weight is not used).
    @type  waut: L{Automaton}

    @param wvalues: Column matrix data, associated with each state in L{waut}.
    @type  wvalues: L{maxplus.DataCollection}

    @param evtdata: Event information.
    @type  evtdata: L{EventData}

    @param num_res: Number of resources.
    @type  num_res: C{int}

    @param start: Start vector (row-matrix), if specified.
    @type  start: C{None}, or L{maxplus.DataCollection}

    @return: Reduced automaton.
    @rtype:  L{Automaton}
    """
    waut = waut.copy() # Make a copy
    wvalues = dict((st.number, val) for st, val in wvalues.iteritems())

    # Do a breadth-first expansion over the automaton.

    #: Mapping of states to their row matrix value.
    seen_states = set([waut.initial])
    not_done = [waut.initial]

    while len(not_done) > 0:
        # Since we do a breadth-first expansion, make a new 'not_done'
        # from scratch on each iteration.
        new_not = []
        for state in not_done:
            rval = maxplus.make_rowmat(0, num_res)
            sval = maxplus.otimes_mat_mat(rval, wvalues[state.number])

            for edge in list(state.get_outgoing()):
                result = maxplus.otimes_mat_mat(rval,
                                                evtdata[edge.label].matHat)
                cm = maxplus.otimes_mat_mat(result, wvalues[edge.succ.number])
                if cm.get_scalar() <= sval.get_scalar():
                    # Keep the edge.
                    if edge.succ not in seen_states: # It is a new state.
                        seen_states.add(edge.succ)
                        new_not.append(edge.succ)
                else:
                    # Drop the edge.
                    waut.remove_edge(edge)

        # Next iteration.
        not_done = new_not

    waut.reduce(True, True)
    return waut

def reduce_automaton_row_vecors(waut, wvalues, evtdata, num_res, rvecs):
    """
    Reduce the weighted automaton.

    @param waut: (Weighted) automaton (the weight is not used).
    @type  waut: L{Automaton}

    @param wvalues: Column matrix data, associated with each state in L{waut}.
    @type  wvalues: L{maxplus.DataCollection}

    @param evtdata: Event information.
    @type  evtdata: L{EventData}

    @param num_res: Number of resources.
    @type  num_res: C{int}

    @param start: Start vector (row-matrix), if specified.
    @type  start: C{None}, or L{maxplus.DataCollection}

    @return: Reduced automaton.
    @rtype:  L{Automaton}
    """
    waut = waut.copy() # Make a copy
    wvalues = dict((st.number, val) for st, val in wvalues.iteritems())

    # Do a breadth-first expansion over the automaton.

    #: Mapping of states to their row matrix value.
    seen_states = set([waut.initial])
    not_done = [waut.initial]

    while len(not_done) > 0:
        # Since we do a breadth-first expansion, make a new 'not_done'
        # from scratch on each iteration.
        new_not = []
        for state in not_done:
            #rval = maxplus.make_rowmat(0, num_res)
            rval =  rvecs[state]
            sval = maxplus.otimes_mat_mat(rval, wvalues[state.number])

            for edge in list(state.get_outgoing()):
                result = maxplus.otimes_mat_mat(rval,
                                                evtdata[edge.label].matHat)
                cm = maxplus.otimes_mat_mat(result, wvalues[edge.succ.number])
                if cm.get_scalar() <= sval.get_scalar():
                    # Keep the edge.
                    if edge.succ not in seen_states: # It is a new state.
                        seen_states.add(edge.succ)
                        new_not.append(edge.succ)
                else:
                    # Drop the edge.
                    waut.remove_edge(edge)

        # Next iteration.
        not_done = new_not

    waut.reduce(True, True)
    return waut

