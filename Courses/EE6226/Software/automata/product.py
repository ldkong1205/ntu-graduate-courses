#
# $Id: product.py 601 2010-01-20 14:54:03Z hat $
#
"""
Compute product of two automata
"""
from automata import common, algorithm

def n_ary_unweighted_product(auts, delete_aut = False,
                             report_progress = False, preserve_names = False):
    """
    N-ary unweighted automata product.

    @param auts: Input automata.
    @type  auts: C{list} of L{Automaton}

    @param delete_aut: Routine is allowed to delete the provided automata.
    @type  delete_aut: C{bool}

    @param report_progress: Output progress of the computation.
    @type  report_progress: C{bool}

    @param preserve_names: Try to preserve state names in the product.
    @type  preserve_names: C{bool}

    @return: Resulting unweighted automaton.
    @rtype:  L{Automaton}
    """
    if report_progress:
        common.print_line("Computing product of %d unweighted automata"
                                                                % len(auts))

    if len(auts) == 1:
        return auts[0]

    prod, mapping = n_ary_unweighted_product_map(auts, preserve_names)

    del mapping
    if delete_aut:
        for aut in auts:
            aut.clear()

    return prod


def n_ary_unweighted_product_map(auts, preserve_names = False):
    """
    N-ary unweighted automata product.

    @param auts: Input automata.
    @type  auts: C{list} of L{Automaton}

    @param preserve_names: Try to preserve state names in the product.
    @type  preserve_names: C{bool}

    @return: Resulting unweighted automaton, and state map.
    @rtype:  L{Automaton}, C{dict} of C{tuple} of L{BaseState} to L{BaseState}
    """
    props = algorithm.ManagerProperties(auts[0].collection)
    props.aut_type = algorithm.UNWEIGHTED_AUT
    props.marker_func = algorithm.MARKED_ALL
    props.explore_mgr = algorithm.ORIGINAL_STATE
    props.edge_calc = algorithm.COPY_LABEL

    return do_n_ary_product_map(props, auts, preserve_names)

def do_n_ary_product_map(props, auts, preserve_names):
    """
    Perform n-ary product calculation both for unweighted and weighted automata.

    @param props: Manager properties controlling the computation, except for
                  the resulting alphabet.
    @type  props: L{ManagerProperties}

    @param auts: Input automata.
    @type  auts: C{list} of L{BaseAutomaton}

    @param preserve_names: Try to preserve state names in the product.
    @type  preserve_names: C{bool}

    @return: Resulting automaton, and state map.
    @rtype:  L{BaseAutomaton},
             C{dict} of (C{tuple} of L{BaseState}) to L{BaseState}

    @note: The alphabet of the resulting automaton is inserted into the
           properties by the function.
    """
   # assert len(auts) >= 2

    has_plant, has_req, has_other = False, False, False
    result_alphabet = set()
    for aut in auts:
        # Verify that all automata use the same collection, and have an initial
        # state.
        assert aut.collection is auts[0].collection
        assert aut.initial is not None

        result_alphabet.update(aut.alphabet)

        if aut.aut_kind == 'plant':
            has_plant = True
        elif aut.aut_kind == 'requirement':
            has_req = True
        else:
            has_other = True

    props.alphabet = result_alphabet

    if has_plant and not has_req and not has_other:
        result_kind = 'plant'
    elif not has_plant and has_req and not has_other:
        result_kind = 'requirement'
    else:
        result_kind = 'unknown'

    # Construct a mapping from event to a boolean whether or not each automaton
    # participates with the event.
    participate = {}
    for evt in result_alphabet:
        participate[evt] = [evt in aut.alphabet for aut in auts]

    mgr = algorithm.Manager(props)
    mgr.set_initial(tuple(aut.initial for aut in auts))
    while True:
        orig_state = mgr.get_next()
        if orig_state is None:
            break

        # Find current edges, collect disabled events from the orig_state.
        edges = [] #: List of lists with edges of each automaton.
        disabled = set() #: Disabled events
        for aut, state in zip(auts, orig_state):
            aut_edges = []
            aut_events = set()
            for edge in state.get_outgoing():
                aut_edges.append(edge)
                aut_events.add(edge.label)

            edges.append(aut_edges)
            disabled.update(aut.alphabet.difference(aut_events))

        # Do every event that is enabled.
        for evt in result_alphabet.difference(disabled):
            add_new_states(orig_state, evt, participate[evt], edges, mgr,
                           [], [])

    prod_aut = mgr.get_automaton()
    prod_aut.aut_kind = result_kind
    mapping = mgr.get_mapping()

    if preserve_names:
        # Construct 'nice' human readable state names in the product.
        for aut in auts:
            aut.make_state_names_complete()

        destnames = set(prod_aut.state_names.itervalues())
        for origstates, deststate in mapping.iteritems():
            name = "-".join(aut.state_names[state.number]
                            for aut, state in zip(auts, origstates))
            if name not in destnames:
                if deststate.number in prod_aut.state_names:
                    destnames.remove(prod_aut.state_names[deststate.number])
                destnames.add(name)
                prod_aut.set_state_name(deststate, name)

        del destnames

    return prod_aut, mapping


def add_new_states(orig_state, evt, participates, all_edges, mgr,
                   old_dest, old_edges):
    """
    Add new states to L{mgr} when performing a transition labeled L{evt} over
    L{all_edges} from L{orig_state}.

    @param orig_state: Original state.
    @type  orig_state: C{list} of L{BaseState}

    @param evt: Event to perform.
    @type  evt: L{Event}

    @param participates: Booleans which automata participate in event L{evt}.
    @type  participates: C{list} of C{bool}

    @param all_edges: All edges available from the original state, ordered by
                      automaton.
    @type  all_edges: C{list} of C{list} of L{Edge}

    @param mgr: Manager constructing the resulting automaton, and keeping track
                of the unexplored states.
    @type  mgr: L{Manager}

    @param old_dest: Destination state being constructed.
    @type  old_dest: C{list} of L{BaseState}

    @param old_edges: Perticipating edges.
    @type  old_edges: C{list} of L{Edge}
    """
    if len(old_dest) == len(orig_state):
        # Step is complete, add it to the mgr.
        mgr.add_edge(orig_state, tuple(old_dest), old_edges)
        return

    idx = len(old_dest)
    if participates[idx]:
        for edge in all_edges[idx]:
            if edge.label == evt:
                add_new_states(orig_state, evt, participates, all_edges, mgr,
                               old_dest + [edge.succ], old_edges + [edge])
    else:
        add_new_states(orig_state, evt, participates, all_edges, mgr,
                       old_dest + [orig_state[idx]], old_edges)


def reverse_statemap(state_map):
    """
    Compute and return a reversed mapping of the state map.

    @param state_map: Mapping of input automata states to output states.
    @type  state_map: C{dict} of C{tuple} (L{State}, L{State}) to L{State}

    @return: Reverse mapping of state in the output automaton to the
             pair of states in the input automata.
    @rtype:  C{dict} of L{State} to C{tuple} (L{State}, L{State})
    """
    rev_map = {}
    for key, val in state_map.iteritems():
        rev_map[val] = key

    return rev_map
