#
# $Id: abstraction.py 740 2010-05-20 13:54:15Z hat $
#
from automata import product, collection, common, data_structure, \
                     exceptions

# {{{ def order_automata(aut_list):
def order_automata(aut_list):
    """
    Use a heuristic to order automata for reduced memory and CPU usage during
    computations.

    @param aut_list: List of arbitrarily ordered automata
    @type  aut_list: C{list} L{Automaton}

    @return: Heuristically ordered automata list
    @rtype: C{list} L{Automaton}
    """
    processed = []
    while len(processed) < len(aut_list):

        # Compute the set of events used by the already processed automata
        events = set()
        for aut in processed:
            events.update(aut.alphabet)

        # Find the unprocessed automaton that gives greatest reduction in
        # coupled events
        # (ie after addition, we should as few common events as possible
        #  between processed and unprocessed automata)
        best = None
        best_ratio = None

        # Try each unprocessed automaton
        for aut in aut_list:
            if aut in processed:
                continue

            # Compute the set of events of processed automata after adding 'aut'
            new_events = events.union(aut.alphabet)
            count_new_events = len(new_events)

            # Compute set of events used by unprocessed automata after 'adding'
            # automaton 'aut'
            unprocessed_events = set()
            for aut2 in aut_list:
                if aut is not aut2 and aut2 not in processed:
                    unprocessed_events.update(aut2.alphabet)

            # Compute ratio for 'aut'
            count_new_common = len(new_events.intersection(unprocessed_events))
            ratio = float(count_new_common)/float(count_new_events)

            # If better, mark 'aut' as our candidate
            if best is None or best_ratio > ratio:
                best = aut
                best_ratio = ratio

        assert best is not None
        processed.append(best)

    return processed

# }}}

# {{{ def bisimilarity_partition(aut):
def bisimilarity_partition(aut):
    """
    Partition states of the automaton based on bisimilarity for the purpose
    of abstraction.

    @param aut: Automaton.
    @type  aut: L{BaseAutomaton}

    @return: State partitions.
    @rtype: C{list} of C{set} of L{State}
    """
    assert aut.collection.events["tau"] in aut.alphabet

    partition_list, state_function = initialize_partition(aut)
    return create_partitions(aut, partition_list, state_function, aut.alphabet)


def bisimilarity_partition_for_observer_check(aut, observable_events):
    """
    Partition states of L{aut} based on non-observable events for the purpose
    of checking the observability property.

    @param aut: Automaton.
    @type  aut: L{BaseAutomaton}

    @param observable_events: Observable events.
    @type  observable_events: C{set} of L{Event}

    @return: State partitions.
    @rtype: C{list} of C{set} of L{State}
    """
    partition_list, state_function = \
                            initialize_partition_for_observer_check(aut,
                                                            observable_events)

    return create_partitions(aut, partition_list, state_function,
                                                            observable_events)


def initialize_partition(aut):
    """
    Create initial partioning of the automaton states (in marked states and
    non-marked states).

    @param aut: Automaton.
    @type  aut: L{BaseAutomaton}

    @return: Initial partitions.
    @rtype: C{list} of C{set} of L{State}
    """
    marker_states = set()
    nonmarker_states = set()
    for state in aut.get_states():
        if state.marked:
            marker_states.add(state)
        else:
            nonmarker_states.add(state)
    partition_list = []
    state_function = {}
    if len(marker_states) > 0:
        partition_list.append(marker_states)
        partition_number = len(partition_list) - 1
        for state in marker_states:
            state_function[state] = partition_number

    if len(nonmarker_states) > 0:
        partition_list.append(nonmarker_states)
        partition_number = len(partition_list) - 1
        for state in nonmarker_states:
            state_function[state] = partition_number

    return partition_list, state_function


def initialize_partition_for_observer_check(aut, preserved_alphabet):
    """
    Create initial partioning of the automaton states (in states coreachable
    through non-observable events) and states non-coreachable through
    non-observable events).

    @param aut: Automaton.
    @type  aut: L{BaseAutomaton}

    @return: Initial partitions.
    @rtype: C{list} of C{set} of L{State}, C{dict} of L{State} to C{int}
    """
    allowed_events = aut.alphabet.difference(preserved_alphabet)

    marker_states = aut.coreachable_states_set(None, allowed_events)
    nonmarker_states = set(state for state in aut.get_states()
                                 if state not in marker_states)

    partition_list = []
    state_function = {}
    if len(marker_states) > 0:
        partition_list.append(marker_states)
        partition_number = len(partition_list) - 1
        for state in marker_states:
            state_function[state] = partition_number

    if len(nonmarker_states) > 0:
        partition_list.append(nonmarker_states)
        partition_number = len(partition_list) - 1
        for state in nonmarker_states:
            state_function[state] = partition_number

    return partition_list, state_function

def dump_state_function(state_function):
    """
    Output a nicely readable dump of the state function (the state ->
    partition map).

    @param partition_list: Initial state partitions.
    @type  partition_list: C{list} of C{set} of L{State}

    @return: Human readable version of the state function.
    @rtype:  C{str}
    """
    part_states = {}
    for state, part_num in state_function.iteritems():
        states = part_states.get(part_num, [])
        states.append(state.number)
        part_states[part_num] = states

    parts = [(n, sts) for n, sts in part_states.iteritems() if len(sts) > 0]
    parts.sort()
    return "\n".join("\tpartition %d: %s" % partdata for partdata in parts)

def create_partitions(aut, partition_list, state_function, obs_events):
    """
    Compute the fixed point of the partioning.

    @param aut: Automaton being partioned.
    @type  aut: L{BaseAutomaton}

    @param partition_list: Initial state partitions.
    @type  partition_list: C{list} of C{set} of L{State}

    @param state_function: Mapping of state to partition number.
    @type  state_function: C{dict} of L{State} to C{int}

    @param obs_events: Events relevant for the partitioning.
    @type  obs_events: C{set} of L{Event}

    @return: Fixed point partitioning of the states of L{aut}.
    @rtype: C{list} of C{set} of L{State}

    @invariant: state in partition_list[i] <=> state_function[state] == i
    """
    nonobs_events = aut.alphabet.difference(obs_events)

    changed_partitions = []

    # Perform partitioning of the states iteratively
    unfinished = True
    while unfinished:
        unfinished = False
        for evt in obs_events:

            for partition in partition_list:

                # Compute set of ancestor states from partition that have
                # outgoing 'evt'
                if len(nonobs_events) > 0:
                    p_start = aut.coreachable_states_set(partition,
                                                         nonobs_events)
                else:
                    # No events to extend the set, use the original set.
                    p_start = partition

                ancestor_set = set(edge.pred
                                   for state in p_start
                                   for edge in state.get_incoming(evt))

                if len(ancestor_set) == 0:
                    continue

                if len(nonobs_events) > 0:
                    ancestor_set = aut.coreachable_states_set(ancestor_set,
                                                              nonobs_events)

                # Clear existing changed_partitions sets, and optionally
                # extend the list to the new set of partitions
                for partition in changed_partitions:
                    partition.clear()
                while len(changed_partitions) < len(partition_list):
                    changed_partitions.append(set([]))

                # Add successors of all ancestors into the current partitioning
                for state in ancestor_set:
                    changed_partitions[state_function[state]].add(state)

                for i, changed_subset in enumerate(changed_partitions):
                    if len(changed_subset) == 0:
                        continue

                    # If a changed_partitions[] entry has changed (and is
                    # used), we have found a new point to partition on
                    if changed_subset != partition_list[i]:
                        partition_list[i].difference_update(changed_subset)

                        partition_list.append(changed_subset.copy())
                        new_partition_number = len(partition_list) - 1
                        for state in changed_subset:
                            state_function[state] = new_partition_number
                        unfinished = True

                    else:
                        changed_partitions[i].clear()

    return partition_list

# }}} def bisimilarity_partition(aut):

# {{{ def abstraction(aut, preserved_alphabet):
# {{{ def automaton_abstraction(aut):
def automaton_abstraction(aut):
    """
    Compute new automaton by means of bisimularity computation with reduced
    number of states.

    @param aut: Input automaton
    @type  aut: L{Automaton}

    @return: Reduced automaton
    @rtype: L{Automaton}
    """

    # Compute partition
    partition_list = bisimilarity_partition(aut)

    # Construct new automaton based on bisimularity results
    new_aut = data_structure.Automaton(aut.alphabet, aut.collection)
    new_aut.set_kind(aut.aut_kind)

    state_map = {}  # Mapping of old state -> new_state
    for number, partition in enumerate(partition_list):
        # Decide on marker property of the partition
        assert len(partition) > 0
        # Get a value from the set without modifying it
        state = iter(partition).next()

        new_state = new_aut.add_new_state(marked = state.marked, num = number)
        for state in partition:
            state_map[state] = new_state

    # Set initial state
    new_aut.initial = state_map[aut.initial]

    # Add edges
    #
    # Since the Automaton silently drops duplicate edges, we will have unique
    # edges
    for state in aut.get_states():
        for edge in state.get_outgoing():
            new_aut.add_edge_data(state_map[state], state_map[edge.succ],
                                  edge.label)

    # Clearing local data
    state_map.clear()

    return new_aut

# }}} def automaton_abstraction(aut):
# {{{ def model_conversion(aut, preserved_events):
def model_conversion(aut, preserved_events):
    """
    Compute automaton with only observable events.

    @note: If marker events are to be preserved, they should be added to the
           L{preserved_events} by the user.

    @param aut: Original automaton
    @type  aut: L{Automaton}

    @param preserved_events: Observable events
    @type  preserved_events: C{set} of C{Event}

    @return: Reduced automaton
    @rtype: L{Automaton}
    """
    non_preserved_events = aut.alphabet.difference(preserved_events)
    new_aut = data_structure.Automaton(preserved_events, aut.collection)

    def get_new_state(old_state):
        """
        From a state of the old automaton (old_state), return the associated
        state of the new automaton (or create one)
        """
        if not new_aut.has_state(old_state.number):
            new_state = new_aut.add_new_state(marked = old_state.marked,
                                              num = old_state.number)
            return new_state

        return new_aut.get_state(old_state.number)


    for state in aut.get_states():
        for edge in state.get_outgoing():
            if edge.label in preserved_events or edge.label.marker:
                reachables = aut.reachable_states(edge.succ,
                                                          non_preserved_events)
                coreachables = aut.coreachable_states(state,
                                                          non_preserved_events)

                for start_state in coreachables:
                    # Find or create same start state in new automaton
                    new_start = get_new_state(start_state)

                    for dest_state in reachables:
                        # Find or create same dest state in new automaton
                        new_dest = get_new_state(dest_state)
                        new_aut.add_edge_data(new_start, new_dest, edge.label)

                reachables.clear()
                coreachables.clear()

    # Initial state must have a path with an observable event to make the
    # line below hold
    new_aut.set_initial(new_aut.get_state(aut.initial.number))

    valid_aut = new_aut.reduce(reachability = True)
    assert valid_aut == True

    non_preserved_events.clear()
    return new_aut
# }}} def model_conversion(aut, preserved_events):

def abstraction(aut, preserved_alphabet):
    """
    Perform abstraction on automaton (reduce it to alphabet
    L{preserved_alphabet}).

    @param aut: Automaton to abstract.
    @type  aut: L{Automaton}

    @param preserved_alphabet: Set of events to preserve.
    @type  preserved_alphabet: C{set} of L{Event}

    @return: Abstracted automaton.
    @rtype: L{Automaton}
    """

    coll = aut.collection
    has_tau = ('tau' in coll.events and coll.events['tau'] in aut.alphabet)

    if not has_tau:
        aut = add_tau_event(aut)

    preserved_events = preserved_alphabet.copy()
    preserved_events.add(aut.collection.events["tau"])
    converted = model_conversion(aut, preserved_events)

    #print converted.to_dot(True)
    abstracted = automaton_abstraction(converted)

    converted.clear()

    if not has_tau:
        remove_tau(abstracted) # Modifies 'abstracted'

    return abstracted

# }}}
def observer_check(aut, observable_events):
    """
    Verify whether the natural projection from the alphabet of the automaton
    to the preserved alphabet is an observer w.r.t. the marked behaviour
    Lm(aut).

    @param aut: Automaton to abstract.
    @type  aut: L{Automaton}

    @param observable_events: Set of observable events.
    @type  observable_events: C{set} of L{Event}

    @return: The set of events that break the observer property.
    @rtype:  C{set} of L{Event}
    """
    # Reduce automaton to only the reachable and co-reachable part.
    coreachables = aut.coreachable_states_set(None, None)
    if len(coreachables) != aut.get_num_states():
        msg = "Automaton is not coreachable, please trim it first."
        raise exceptions.ModelError(msg)

    partitions = bisimilarity_partition_for_observer_check(aut,
                                                           observable_events)

    bad_events = set()
    allowed_events = aut.alphabet.difference(observable_events)
    for partition in partitions:
        for state in partition:
            for edge in state.get_outgoing():
                if edge.label not in allowed_events:
                    continue

                if edge.succ not in partition:
                    bad_events.add(edge.label)

    return bad_events



# {{{ def sequential_abstraction(automata_list, target_events):

def compute_t(i, automata_list, target_events):
    """
    Compute alphabet needed for processing L{automata_list}[i-1] in the
    sequential abstraction procedure.

    @param i: Number of the automaton in the L{automata_list}
    @type  i: C{int} in range(1, len(automata_list)+1)

    @param automata_list: List of automata
    @type  automata_list: C{list} of L{Automaton}

    @param target_events: List of events to preserve after abstraction
    @type  target_events: C{set} of L{Event}

    @return: New alphabet for the next step in sequential abstraction
    @rtype: C{set} of L{Event}
    """
    processed = set()
    for j in range(0, i):
        processed = processed.union(automata_list[j].alphabet)

    unprocessed = target_events.copy()
    for j in range(i, len(automata_list)):
        unprocessed = unprocessed.union(automata_list[j].alphabet)

    result = processed.intersection(unprocessed)

    processed.clear()
    unprocessed.clear()
    return result


def sequential_abstraction(automata_list, target_events):
    """
    Perform a sequence of abstraction and product computation steps

    @param automata_list: List of automata
    @type  automata_list: C{list} of L{Automaton}

    @param target_events: List of events to preserve after abstraction
    @type  target_events: C{set} of L{Event}

    @return: An automaton
    @rtype: L{Automaton}
    """
    assert len(automata_list) > 0

    coll = automata_list[0].collection
    common.print_line("Started")

    # Paranoia check, all automata should use the same collection
    for aut in automata_list:
        assert aut.collection is coll

    # Setup for first automaton
    k = 1
    t_k = compute_t(1, automata_list, target_events)
    aut_k = automata_list[k - 1]
    msg = "#states after adding %d automata: %d" % (k, aut_k.get_num_states())
    common.print_line(msg)

    result = abstraction(aut_k, t_k)

    msg = "#states and #transitions after abstraction: %d, %d" \
                            % (result.get_num_states(), result.get_num_edges())
    common.print_line(msg)
    k = k + 1

    # For each automaton 2..len(automata_list) (including upper-bound)
    while k <= len(automata_list):
        prev_result = result

        aut_k = automata_list[k - 1]

        prod = product.n_ary_unweighted_product([prev_result, aut_k])

        msg = "#states of %d automata: %d; #states and #transitions " \
              "of product: %d %d" % (k, aut_k.get_num_states(),
                                    prod.get_num_states(), prod.get_num_edges())
        common.print_line(msg)

        t_k = compute_t(k, automata_list, target_events)
        result = abstraction(prod, t_k)

        msg = "#states and #transitions after abstraction: %d, %d" \
                            % (result.get_num_states(), result.get_num_edges())
        common.print_line(msg)

        # Remove intermediate results from collection
        prev_result.clear()
        prod.clear()

        k = k + 1

    return result

# }}} def sequential_abstraction(automata_list, target_events):

# {{{ def add_tau_event(aut):
def add_tau_event(aut, always_make_copy = False, add_marker_events = False):
    """
    Ensure 'tau' event is available, if needed by making a new automaton

    @param aut: Existing automaton
    @type  aut: L{Automaton}

    @param always_make_copy: Always make a copy of the automaton, even if
                             nothing changes.
    @type  always_make_copy: C{bool}

    @param add_marker_events: Add marker events to the automaton.
                              Needs L{always_make_copy}.
    @type  add_marker_events: C{bool}

    @return: Existing automaton if 'tau' event exists, otherwise a new
             automaton with 'tau' as additional event in the alphabet, and a
             new initial state that leads to the old initial state with a
             'tau' edge.
    @rtype: L{Automaton}
    """
    # Check 'add_marker_events => always_make_copy'
    assert not add_marker_events or always_make_copy

    tau_evt = get_tau_event(aut.collection)

    # Tau event already in the automaton -> do nothing
    if tau_evt in aut.alphabet:
        if always_make_copy:
            return aut.copy(add_marker_events = add_marker_events)
        return aut

    new_aut = aut.copy(add_marker_events = add_marker_events)

    new_aut.alphabet.add(tau_evt)
    assert new_aut.initial is not None
    new_start = new_aut.add_new_state(marked = False)
    new_aut.add_edge_data(new_start, new_aut.initial, tau_evt)
    new_aut.initial = new_start

    return new_aut

# }}} def add_tau_event(aut)
# {{{ def remove_tau(aut):
def remove_tau(aut):
    """
    Modify automaton in-place, removing the 'tau' event.
    Will fail if there is more than one otgoing 'tau' event.

    @param aut: Existing automaton.
    @type  aut: L{BaseAutomaton}
    """
    coll = aut.collection
    tau_event = coll.events['tau']

    # Count edges from initial state
    tau_edge_count = 0   #: Number of 'tau' edges.
    tau_edge_dest = None #: A destination of a 'tau' edge.
    for edge in aut.initial.get_outgoing():
        assert edge.label is tau_event
        tau_edge_count = tau_edge_count + 1
        tau_edge_dest = edge.succ

    if tau_edge_count > 1:
        msg = "Cannot remove 'tau' event, there are %d 'tau' edges from " \
              "initial state while expected exactly one." % tau_edge_count
        raise exceptions.ModelError(msg)

    assert tau_edge_dest != aut.initial
    aut.remove_state(aut.initial)
    aut.set_initial(tau_edge_dest)

    # Check there are no other 'tau' events in the automaton.
    for state in aut.get_states():
        for edge in state.get_outgoing():
            assert edge.label is not tau_event

    aut.alphabet.remove(tau_event)

# }}}
# {{{ def get_tau_event(collection):
def get_tau_event(coll):
    """
    Get the 'tau' event from the collection if it exists.
    Otherwise, create it first.

    @param coll: Event collection.
    @type  coll: L{Collection}

    @return: Tau event of the collection.
    @rtype:  L{Event}
    """
    if 'tau' not in coll.events:
        tau_evt = collection.Event('tau', False, False, False)
        coll.add_event(tau_evt)
    else:
        tau_evt = coll.events['tau']

    assert not tau_evt.controllable
    assert not tau_evt.observable
    assert not tau_evt.marker

    return tau_evt
# }}}

# {{{ def nonconflicting_check(automata_list):
def calc_non_coreachables(aut):
    """
    Return the set of states that are not co-reachable in the automaton

    @param aut: Automaton to use
    @type  aut: L{Automaton}

    @return: Set of non co-reachable states
    @rtype: C{set} of L{State}
    """
    coreachable_states = set()
    for state in aut.get_states():
        if state.marked and state not in coreachable_states:
            coreachable_states.update(aut.coreachable_states(state, None))
            if len(coreachable_states) == aut.get_num_states():
                return set()  # All states are reachable

    non_coreachable_states = set()
    for state in aut.get_states():
        if state not in coreachable_states:
            non_coreachable_states.add(state)

    # Clear locally computed data
    coreachable_states.clear()

    return non_coreachable_states


def nonconflicting_check(automata_list):
    """
    Check that automata in L{automata_list} are non-conflicting

    @param automata_list: List of automata to verify
    @type  automata_list: C{List} of L{Automaton}

    @return: Boolean indicating non-conflicting automata
    @rtype: C{bool}
    """

    assert len(automata_list) > 0

    # Add Tau event if needed to all automata
    new_auts = [add_tau_event(aut, always_make_copy = True,
                                   add_marker_events = True)
                                                for aut in automata_list]

    coll = automata_list[0].collection
    tau_evt = coll.events['tau']

    # Remove internal behavior of each automaton
    for idx, new_aut in enumerate(new_auts):
        others_events = set()
        for other_aut in new_auts:
            if other_aut is not new_aut:
                others_events.update(other_aut.alphabet)
        ext_events = others_events.intersection(new_aut.alphabet)
        new_auts[idx] = abstraction(new_aut, ext_events)
        new_aut.clear() # Remove old automaton

    #print new_auts[0].to_dot(True)
    seqabs = sequential_abstraction(new_auts,
                                    set([tau_evt, coll.marker_event]))

    non_coreachables = calc_non_coreachables(seqabs)
    return len(non_coreachables) == 0

# }}} def nonconflicting_check(automata_list):
