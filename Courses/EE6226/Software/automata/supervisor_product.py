#
# $Id: supervisor_product.py 672 2010-03-24 10:26:31Z hat $
#
"""
Compute product of two automata
"""
from automata import algorithm, common, exceptions

DBG = 0

def coreachable_bad_states(aut, bad_states, usable_events):
    """
    Find all states that are co-reachable from one of the L{bad_states} while
    only traversing edges with non-controllable events from the
    L{usable_events} set.

    @param aut: Automaton to use.
    @type  aut: L{Automaton}

    @param bad_states: Set bad states to extend.
    @type  bad_states: C{set} of L{State} (of L{aut})

    @param usable_events: Set of events that may be traversed.
    @type  usable_events: C{set} of L{Event}

    @return: Extended set of bad states
    @rtype: C{set} of L{State}
    """
    if len(bad_states) == 0 or len(usable_events) == 0:
        return bad_states

    usable_events = set(evt for evt in usable_events if not evt.controllable)
    usable_events.discard(aut.collection.marker_event)

    if len(usable_events) == 0:
        return bad_states

    states = set()
    for bad_state in bad_states:
        if bad_state not in states:
            states.update(aut.coreachable_states(bad_state, usable_events))
        # else: bad_state was already explored from another bad state

    usable_events.clear()

    return states


def supervisor_product(comp, comp_bad, compreq, compreq_is_requirement,
                       usable_events):
    """
    Perform a product calculation for the purpose of supervisor synthesis.

    @param comp: First automaton, always a component (possbily the result of a
                 previous call).
    @type  comp: L{BaseAutomaton}

    @param comp_bad: Known bad states of L{comp}.
    @type  comp_bad: C{set} of L{BaseState}

    @param compreq: Second automaton, either a component or a requirement.
    @type  compreq: L{BaseAutomaton}

    @param compreq_is_requirement: Second automaton is a requirement automaton.
    @type  compreq_is_requirement: C{bool}

    @param usable_events: Set of events that may be traversed.
    @type  usable_events: C{set} of L{Event}

    @return: Resulting automaton, and its bad state set.
    @rtype:  L{BaseAutomaton}, C{set} of L{BaseState}

    @note: The alphabet of the resulting automaton is inserted into the
           properties by the function.

    @precond: If L{compreq_is_requirement}, the alphabet of L{compreq} must be
              a subset of L{comp}.
    """
    # Generate progress message.
    if compreq_is_requirement:
        compreq_text = "spec"
    else:
        compreq_text = "plant"

    msg = "Start supervisor product %d states (%d bad) with %s %d states" \
          % (comp.get_num_states(), len(comp_bad),
             compreq_text, compreq.get_num_states())
    common.print_line(msg)


    props = algorithm.ManagerProperties(comp.collection)
    props.aut_type = algorithm.UNWEIGHTED_AUT
    props.marker_func = algorithm.MARKED_ALL
    props.explore_mgr = algorithm.ORIGINAL_STATE
    props.edge_calc = algorithm.COPY_LABEL

    result_alphabet = comp.alphabet.union(compreq.alphabet)
    props.alphabet = result_alphabet

    compreq_only_alphabet = compreq.alphabet.difference(comp.alphabet)

    # Either compreq is not a requirement, or it has no edges of its own.
    assert not compreq_is_requirement or len(compreq_only_alphabet) == 0

    bad_states = set() #: New bad states, list of original state combinations.

    mgr = algorithm.Manager(props)
    mgr.set_initial((comp.initial, compreq.initial))
    while True:
        orig_state = mgr.get_next()
        if orig_state is None:
            break

        # If it was a bad state previously, it will be again.
        if orig_state[0] in comp_bad:
            # Reset marker property of bad state.
            state = mgr.state_mgr.mapping[orig_state]
            state.marked = False
            bad_states.add(state)
            continue # Pick the next one.


        #: Available compreq edges ordered by event-name.
        compreq_event_edges = {}
        for edge in orig_state[1].get_outgoing():
            edges = compreq_event_edges.get(edge.label)
            if edges is None:
                edges = []
                compreq_event_edges[edge.label] = edges
            edges.append(edge)

        if compreq_is_requirement:
            # If compreq is a requirement, look whether we are at a bad state.
            # Those happen when the event is enabled in comp, disabled in
            # compreq, and the event is uncontrollable (ie from the current
            # state, we disable an uncontrollable event by a spec). In that
            # case, the current state in the product is bad (it violates the
            # controllability property). Add the product state to the bad
            # states.

            # Decide whether it is a bad state.
            bad_state = False
            for edge in orig_state[0].get_outgoing():
                # The edge label is controllable, or
                # compreq also has an outgoing edge for this event, or
                # the label is not in the compreq alphabet.
                if edge.label.controllable or \
                        edge.label in compreq_event_edges or \
                        edge.label not in compreq.alphabet:
                    continue

                bad_state = True
                break

            if bad_state:
                # Reset marker property of bad state.
                state = mgr.state_mgr.mapping[orig_state]
                state.marked = False
                bad_states.add(state)
                continue # Do not expand current state, pick the next one.

        # A good state, expand to new states.

        # Expand edges of first automaton.
        for edge in orig_state[0].get_outgoing():
            if edge.label not in compreq.alphabet: # comp only.
                mgr.add_edge(orig_state, (edge.succ, orig_state[1]), [edge])
                continue

            compreq_edges = compreq_event_edges.get(edge.label)
            if compreq_edges is None:
                # Disabled by compreq, but not in a bad way.
                continue

            for edge2 in compreq_edges:
                mgr.add_edge(orig_state,
                             (edge.succ, edge2.succ), [edge, edge2])

        # Perform compreq only
        for evt in compreq_only_alphabet:
            compreq_edges = compreq_event_edges.get(evt)
            if compreq_edges is not None:
                for edge2 in compreq_edges:
                    mgr.add_edge(orig_state,
                                 (orig_state[0], edge2.succ), [edge2])

    # Finished with the product.

    prod_aut = mgr.get_automaton()
    prod_aut.aut_kind = 'supervisor'

    mgr.get_mapping().clear()

    # Do a co-reachability search, and trim out all states AFTER the initial
    # non-coreachable state. The initial non-coreachable states must be added
    # to the bad states as well.

    # Compute co-reachable set of the product.
    coreachables = set()
    not_done = []
    for state in prod_aut.get_states():
        if state.marked:  # Bad states are never marked.
            coreachables.add(state)
            not_done.append(state)

    if len(not_done) == 0:
        # No marker states at all in the product
        msg = "Supervisor product is empty (no marker states in the product)."
        raise exceptions.ModelError(msg)

    while len(not_done) > 0:
        state = not_done.pop()
        for edge in state.get_incoming():
            if edge.pred not in coreachables:
                coreachables.add(edge.pred)
                not_done.append(edge.pred)

    # Finished, all states are coreacahable.
    # Will probably not happen often due to bad states.
    if len(coreachables) == prod_aut.get_num_states():
        assert len(bad_states) == 0
        if DBG:
            common.print_line("Finished, %d states, no bad states"
                              % prod_aut.get_num_states())
        coreachables.clear()
        return prod_aut, bad_states

    # Non-coreachables that have a co-reachable predecessor are bad too.
    non_coreachables = []
    for state in prod_aut.get_states():
        if state in coreachables:
            continue
        if state in bad_states:
            continue

        pred_coreachable = False
        for edge in state.get_incoming():
            if edge.pred in coreachables:
                pred_coreachable = True
                break

        if pred_coreachable:
            bad_states.add(state)
            # Reset marker property of bad state.
            state.marked = False
            # Remove all outgoing edges of the new bad state.
            for edge in list(state.get_outgoing()):
                prod_aut.remove_edge(edge)
        else:
            non_coreachables.append(state)

    coreachables.clear()

    # Remove states that are not bad and not co-reachable.
    for state in non_coreachables:
        if state not in bad_states:
            prod_aut.remove_state(state)

    del non_coreachables

    # Extend the number of bad states by walking backwards over
    # 'usable_events'.
    illegal_states = coreachable_bad_states(prod_aut, bad_states,
                                             usable_events)

    if illegal_states == bad_states:
        if DBG:
            common.print_line("Finished, %d states (%d bad)"
                              % (prod_aut.get_num_states(), len(bad_states)))
        return prod_aut, bad_states


    # Found new illegal states.
    assert bad_states.issubset(illegal_states)

    bad_states = set()
    for state in illegal_states:
        # Check whether 'state' has an anchestor state which is good.
        found_good_state = False
        for edge in state.get_incoming():
            if edge.pred not in illegal_states:
                found_good_state = True
                break

        if found_good_state:
            bad_states.add(state)
            # Reset marker property of bad state.
            state.marked = False
            # Remove all outgoing edges of the new bad state.
            for edge in list(state.get_outgoing()):
                prod_aut.remove_edge(edge)
        else:
            prod_aut.remove_state(state)

    illegal_states.clear()

    if DBG:
        common.print_line("Finished, %d states (%d bad)"
                          % (prod_aut.get_num_states(), len(bad_states)))
    return prod_aut, bad_states

