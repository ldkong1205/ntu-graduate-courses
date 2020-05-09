#
# $Id: supervisor.py 773 2011-07-14 13:01:31Z hat $
#
"""
Supervisor synthesis functions
"""
from automata import product, common, data_structure, exceptions, algorithm, \
                     supervisor_product

DBG = 0

def compute_coupling_ratio(alphabet1, alphabet2):
    """
    Compute the amount of coupling between two alphabets.

    @param alphabet1: First alphabet.
    @type  alphabet1: C{set} of L{Event}

    @param alphabet2: Second alphabet.
    @type  alphabet2: C{set} of L{Event}

    @return: Amount of coupling.
    @rtype:  C{float}
    """
    num_common = float(sum(1 for evt in alphabet1 if evt in alphabet2))
    total = float(len(alphabet1.union(alphabet2)))
    return num_common / total

def get_best_coupled_automaton(alphabet, auts):
    """
    Get the automaton from L{auts} with the best (highest) coupling ratio with
    respect to L{alphabet}.

    @param alphabet: Alphabet to couple against.
    @type  alphabet: C{set} of L{Event}

    @param auts: Automata to select from.
    @type  auts: C{List} of L{BaseAutomaton}

    @return: Selected automaton from L{auts} and its ratio.
    @rtype:  L{BaseAutomaton}, C{float}

    @precond: L{auts} must not be empty.
    """
    best_ratio = None
    best_aut = None
    for aut in auts:
        ratio = compute_coupling_ratio(alphabet, aut.alphabet)
        if best_ratio is None or best_ratio < ratio:
            best_ratio = ratio
            best_aut = aut
        elif best_ratio == ratio and \
                aut.get_num_states() < best_aut.get_num_states():
            best_aut = aut # Smaller automaton is better.

    assert best_aut is not None
    return best_aut, best_ratio

def order_plants(plants):
    """
    Order the plant components.

    @param plants: Components to order.
    @type  plants: C{set} of L{BaseAutomaton}

    @return: Ordered plant automata.
    @rtype:  C{list} of L{BaseAutomaton}
    """
    if len(plants) == 1:
        return list(plants)

    best_ratio = None
    best_pair = None

    plantlist = list(plants)
    for idx, aut1 in enumerate(plantlist[:-1]):
        aut, ratio = get_best_coupled_automaton(aut1.alphabet,
                                                plantlist[idx + 1:])
        if best_ratio is None or best_ratio < ratio:
            best_ratio = ratio
            best_pair = (aut1, aut)

    del plantlist

    assert best_pair is not None
    plants.remove(best_pair[0])
    plants.remove(best_pair[1])

    ordered_plants = list(best_pair)
    alphabet = ordered_plants[0].alphabet.union(ordered_plants[1].alphabet)
    while len(plants) > 0:
        plant, _ratio = get_best_coupled_automaton(alphabet, plants)
        plants.remove(plant)
        ordered_plants.append(plant)
        alphabet.update(plant.alphabet)

    del alphabet
    return ordered_plants

def add_fixated_events(plants):
    """
    Add a field to the elements of a sequence of automata, containing the
    events that are not used by automata futher down the list.

    @param plants: Ordered automata.
    @type  plants: C{list} of L{BaseAutomaton}

    @return: Ordered pairs of automaton, fixated events.
    @rtype:  C{list} of C{tuple} (L{BaseAutomaton}, C{set} of L{Event})
    """
    total_alphabet = set()
    for plant in plants:
        total_alphabet.update(plant.alphabet)

    # This can be done faster by computing from the end, and moving towards
    # the start.
    result = []
    for idx, plant in enumerate(plants):
        fixated = total_alphabet.copy()
        for pl in plants[idx + 1:]:
            fixated.difference_update(pl.alphabet)

        result.append((plant, fixated))
        fixated = None

    total_alphabet.clear()
    return result

def insert_requirements(fixated_plants, reqs):
    """
    Insert each requirement as near to the start as possible in the
    L{fixated_plants} sequence.

    @param fixated_plants: Ordered pairs of automaton, fixated events.
    @type  fixated_plants: C{list} of C{tuple}
                           (L{BaseAutomaton}, C{set} of L{Event})

    @param reqs: Requirements to insert.
    @type  reqs: C{set} of L{BaseAutomaton}

    @return: Ordered triplets of automaton, is specification, fixated events.
    @rtype:  C{list} of C{tuple} (L{BaseAutomaton}, C{bool}, 
             C{set} of L{Event})
    """
    reqs = reqs.copy()

    result = []
    for pl, fixated in fixated_plants:
        result.append((pl, False, fixated))

        # Next, try to add as many requirements as possible.
        # 'fixated' contains the set of events that the requirement may use.
        found_req = True
        while found_req:
            found_req = False
            for req in reqs:
                if req.alphabet.issubset(fixated):
                    found_req = True
                    result.append((req, True, fixated))
                    reqs.remove(req)
                    break

    return result


def compute_products(plants, specs):
    """
    Perform the product for the purpose of supervisor synthesis by sequentially
    computing products of all L{plants} and L{specs}.

    @param plants: Plant automata.
    @type  plants: C{list} of L{BaseAutomaton}

    @param specs: Requirement automata.
    @type  specs: C{list} of L{BaseAutomaton}

    """
    assert len(plants) > 0 # Need at least one plant component.

    plants = set(plants)
    specs  = set(specs)

    # Check alphabets
    plant_alphabet = set() #: Alphabet of the merged components.
    for plant in plants:
        plant_alphabet.update(plant.alphabet)

    for spec in specs:
        bad_events = spec.alphabet.difference(plant_alphabet)
        if len(bad_events) == 1:
            msg = "Event %r from the specification is not in the alphabet " \
                  "of the plant." % bad_events.pop().name
            raise exceptions.ModelError(msg)

        elif len(bad_events) > 1:
            msg = "Events %s from the specification are not in the " \
                  "alphabet of the plant." % ", ".join(repr(event.name)
                                              for event in bad_events)
            raise exceptions.ModelError(msg)

        # else len(bad_events) == 0 -> ok



    ordered_plants = order_plants(plants)
    fixated_plants = add_fixated_events(ordered_plants)

    del plants
    del ordered_plants


    #: Order to compute the supervisor product.
    prod_order = insert_requirements(fixated_plants, specs)

    del fixated_plants
    del specs

    if DBG:
        for comp in prod_order:
            aut = comp[0]
            aut_type = "Plant"
            if comp[1]:
                aut_type = "Specification"

            print "%s %s" % (aut_type, aut.name)
            print "\t#states :", aut.get_num_states()
            print "\t#trans  :", aut.get_num_edges()
            print "\talphabet:", sorted(evt.name for evt in aut.alphabet)
            print "\tFixated events:", sorted(evt.name for evt in comp[2])


    result = None
    idx = 1
    preserve_result = True
    for aut, aut_is_spec, fixated in prod_order:
        aut_type = "requirement" if aut_is_spec else "plant"
        if result is None:
            common.print_line("(%d of %d) Starting with %s %s (%d states)"
                              % (idx, len(prod_order), aut_type, aut.name,
                                 aut.get_num_states()))
            result = aut
            preserve_result = True
            bad_states = set()
        else:
            common.print_line("(%d of %d) Adding %s %s (%d states)"
                              % (idx, len(prod_order), aut_type, aut.name,
                                 aut.get_num_states()))

            result2, bad_states2 = supervisor_product.supervisor_product(
                                                    result, bad_states, aut,
                                                    aut_is_spec, fixated)

            bad_states.clear()
            bad_states = bad_states2
            del bad_states2
            if not preserve_result:
                result.clear()
            result = result2
            del result2
            preserve_result = False

        if result.get_num_states() == 0:
            msg = "Supervisor product is empty (no states in the product)."
            raise exceptions.ModelError(msg)

        idx = idx + 1

    return result, bad_states


# {{{ def controllable_coreachable_product(plants, specs):
def controllable_coreachable_product(plants, specs):
    """
    Compute the controllable and co-reachable sub set of a product.

    @param plants: Plant automata.
    @type  plants: C{list} of L{BaseAutomaton}

    @param specs: Specification automata.
    @type  specs: C{list} of L{BaseAutomaton}

    @return: C{None} if empty automaton reached, or (L{Automaton}, disableds)
             where disableds is a map of automaton states to set of disabled
             events
    """
    prod_aut, bad_states = compute_products(plants, specs)
    prod_aut.reduce(True, False)

    # Construct controllable_states
    uncontrollables = set(evt
                          for evt in prod_aut.alphabet if not evt.controllable)

    controllable_states = set()
    for state in prod_aut.get_states():
        if state not in bad_states:
            controllable_states.add(state)


    while True:

        # Find coreachable states in L{controllable_states}
        coreachable_states = set()
        notdone_list = []
        for state in prod_aut.get_states():
            if state not in controllable_states:
                continue
            if state.marked:
                coreachable_states.add(state)
                notdone_list.append(state)

        while len(notdone_list) > 0:
            state = notdone_list.pop()
            for edge in state.get_incoming():
                if edge.pred not in controllable_states:
                    continue

                if edge.pred not in coreachable_states:
                    coreachable_states.add(edge.pred)
                    notdone_list.append(edge.pred)



        bad_states = supervisor_product.coreachable_bad_states(prod_aut,
                            controllable_states.difference(coreachable_states),
                            uncontrollables)
        if len(bad_states) == 0:
            break

        controllable_states = coreachable_states.difference(bad_states)

        coreachable_states.clear()
        bad_states.clear()



    if prod_aut.initial not in controllable_states:
        return None


    # Construct a new automaton from the reachable and controllable subset
    new_aut = data_structure.Automaton(prod_aut.alphabet, prod_aut.collection)

    def new_state(old_state, new_aut, notdone_list):
        if not new_aut.has_state(old_state.number):
            s = new_aut.add_new_state(old_state.marked, num = old_state.number)
            notdone_list.append(old_state)
            return s
        else:
            return new_aut.get_state(old_state.number)

    # Copy states
    boundary_disableds = {}  # Map of chi states to set of disabled events
    notdone_list = []
    s = new_state(prod_aut.initial, new_aut, notdone_list)
    new_aut.set_initial(s)
    while len(notdone_list) > 0:
        state = notdone_list.pop()
        for edge in state.get_outgoing():
            if edge.succ not in controllable_states:
                # Found an edge that leads to outside the controllable
                # subset, make a note of it

                # Find the same state as 'state' in the new automaton
                equiv_state = new_aut.get_state(state.number)

                if equiv_state not in boundary_disableds:
                    boundary_disableds[equiv_state] = set([edge.label])
                else:
                    boundary_disableds[equiv_state].add(edge.label)

                continue # Ignore the state in the copying process

            new_state(edge.succ, new_aut, notdone_list)

    # Copy edges
    for state in prod_aut.get_states():
        if not new_aut.has_state(state.number):
            continue

        for edge in state.get_outgoing():
            if not new_aut.has_state(edge.succ.number):
                continue

            new_aut.add_edge_data(new_aut.get_state(state.number),
                                new_aut.get_state(edge.succ.number), edge.label)

    prod_aut.clear()

    return new_aut, boundary_disableds
# }}} def controllable_coreachable_product(plants, specs):

# {{{ def make_supervisor(plants, specs):
def make_supervisor(plants, specs):
    """
    Construct a supervisor for the L{plants} that behaves safely within the
    L{specs} requirements.

    @param plants: Plant automata.
    @type  plants: C{list} of L{BaseAutomaton}

    @param specs: Requirements specification automata.
    @type  specs: C{list} of L{BaseAutomaton}

    @return: Supervisor automaton if it exists, C{None} otherwise.
    @rtype: L{Automaton} or C{None}
    """
    assert len(plants) > 0
    assert len(specs) > 0

    # The iteration below replaces the specs by its own automaton.
    # To prevent leaking automata, these own automata should be deleted
    # before exit.
    delete_specs = False

    deterministic_and_all_observable = True
    # Check that all events are observable
    for plant in plants:
        for evt in plant.alphabet:
            if not evt.observable:
                deterministic_and_all_observable = False
                break

    if deterministic_and_all_observable:
        # Check that plant is deterministic
        for plant in plants:
            for state in plant.get_states():
                evts = set() #: Set of events encountered at an edge.
                for edge in state.get_outgoing():
                    if edge.label in evts:
                        deterministic_and_all_observable = False
                        break
                    evts.add(edge.label)

    while True: # make_supervisor() is an iterative function

        result = controllable_coreachable_product(plants, specs)
        if result is None:
            if delete_specs:
                for spec in specs:
                    spec.clear()
            return None

        if deterministic_and_all_observable: # We are finished!
            if delete_specs:
                for spec in specs:
                    spec.clear()
            return result[0]

        chi_aut, boundary_disableds = result

        if len(boundary_disableds) == 0:
            if delete_specs:
                for spec in specs:
                    spec.clear()
            return unweighted_determinization(chi_aut)


        #
        # Construct automaton A
        #
        aut_A = data_structure.Automaton(chi_aut.alphabet.copy(),
                                         chi_aut.collection)

        for state in chi_aut.coreachable_states_set(
                                            set(boundary_disableds.keys()),
                                            None):
            aut_A.add_new_state(marked = False, num = state.number)

        assert aut_A.has_state(chi_aut.initial.number)
        aut_A.set_initial(aut_A.get_state(chi_aut.initial.number))

        # Copy edges
        for state in chi_aut.get_states():
            if not aut_A.has_state(state.number):
                continue

            for edge in state.get_outgoing():
                if not aut_A.has_state(edge.succ.number):
                    continue

                aut_A.add_edge_data(aut_A.get_state(state.number),
                                  aut_A.get_state(edge.succ.number), edge.label)
        # Add dump state
        dump_state = aut_A.add_new_state(True)
        for state, disableds in boundary_disableds.iteritems():
            for disabled in disableds:
                aut_A.add_edge_data(aut_A.get_state(state.number), dump_state,
                               disabled)

        # Self-loops for all events in dump-state
        for evt in aut_A.alphabet:
            aut_A.add_edge_data(dump_state, dump_state, evt)


        A2 = unweighted_determinization(aut_A)
        b = A2.reduce(False, True)
        assert b

        A3 = projection(A2)
        A4 = inverse_projection(A3)

        A2.clear()
        A3.clear()

        A5 = product.n_ary_unweighted_product([chi_aut, A4])


        marked = False
        for state in A5.get_states():
            if state.marked:
                marked = True
                break
        if not marked:
            A4.clear()
            A5.clear()
            if delete_specs:
                for spec in specs:
                    spec.clear()

            return unweighted_determinization(chi_aut)


        A5.clear()

        A6 = complement(A4)
        A7 = unweighted_determinization(
                            product.n_ary_unweighted_product([chi_aut, A6]))
        b = A7.reduce(False, True)
        if not b:
            if delete_specs:
                for spec in specs:
                    spec.clear()
            return None

        A4.clear()
        A6.clear()

        # Iteration:
        # plants = plants
        specs = [A7]
        delete_specs = True

# }}} def make_supervisor(plants, specs):

# {{{ def unweighted_determinization(aut):
def unweighted_determinization(aut):
    """
    Make equivalent deterministic unweighted automaton.

    @param aut: Input automaton.
    @type  aut: L{Automaton}

    @return: Deterministic automaton.
    @rtype: L{Automaton}
    """

    props = algorithm.ManagerProperties(aut.collection)
    props.alphabet = aut.alphabet
    props.aut_type = algorithm.UNWEIGHTED_AUT
    props.marker_func = algorithm.MARKED_ANY
    props.edge_calc = algorithm.COPY_LABEL
    props.explore_mgr = algorithm.ORIGINAL_STATE

    return common_determinization(aut.initial, props)


def common_determinization(initial, props):
    """
    Make equivalent deterministic automaton.

    @param initial: Initial state of the old automaton.
    @type  initial: L{BaseState}

    @param props: Algorithm properties.
    @type  props: L{ManagerProperties}

    @return: Deterministic automaton.
    @rtype: L{BaseAutomaton}

    @note: Used both by unweighted and weighted determinization.
    """
    mgr = algorithm.Manager(props)

    mgr.set_initial(frozenset([initial]))
    while True:
        orig_state_set = mgr.get_next()
        if orig_state_set is None:
            break

        # For all edges of all original states, collect new set of states for
        # each event.

        #: Mapping of event to tuple (set of new states, edges).
        evt_storage = {}
        for orig_state in orig_state_set:
            for edge in orig_state.get_outgoing():
                entry = evt_storage.get(edge.label)
                if entry is None:
                    entry = (set(), [])
                    evt_storage[edge.label] = entry

                entry[0].add(edge.succ)
                entry[1].append(edge)

        # For each event, make a new edge.
        for new_set, edges in evt_storage.itervalues():
            mgr.add_edge(orig_state_set, frozenset(new_set), edges)

    return mgr.get_automaton()

# }}} def unweighted_determinization(aut):
# {{{ def projection(aut):
def projection(aut):
    """
    Project an automaton on not-observable events.

    For each cluster of states (connected with each other through non-observable
    events), find the next cluster for each visible event by computing the
    union of reachable state clusters (from the original cluster, do the
    visible event for all states, and merge all states reachable through
    non-observable events after the transition).
    """
    aut, aut_map = project_map_observables(aut)
    aut_map.clear()
    return aut

def project_map_observables(aut):
    """
    Project an automaton on not-observable events.

    @param aut: Automaton to project.
    @type  aut: L{Automaton}

    @return: Automaton reduced to observable events, and a state map.
    @rtype: L{Automaton}, and a C{dictionary} of a C{set} of L{State} from the
            original automaton to a L{State} in the returned automaton.
    """
    observables = set([evt for evt in aut.alphabet if evt.observable])

    return natural_projection_map(aut, observables)


def natural_projection_map(aut, preserved):
    """
    Project an automaton on preserved events.

    For each cluster of states (connected with each other through non-preserved
    events), find the next cluster for each preserved event by computing the
    union of reachable state clusters (from the original cluster, do the
    preserved event for all states, and merge all states reachable through
    non-preserved events after the transition).

    @param aut: Automaton to project.
    @type  aut: L{Automaton}

    @param preserved: Set of event of the automaton to preserve.
    @type  preserved: C{set} of L{Event}

    @return: Automaton reduced to L{preserved} events, and a state map.
    @rtype: L{Automaton}, and a C{dictionary} of a C{set} of L{State} from the
            original automaton to a L{State} in the returned automaton.
    """
    non_preserved = aut.alphabet.difference(preserved)

    new_aut = data_structure.Automaton(preserved.copy(), aut.collection)

    def add_new_state(states, state_map, new_aut, notdone_list):
        frozen_states = frozenset(states)
        if frozen_states in state_map:
            return state_map[frozen_states]

        marked = False
        for state in states:
            if state.marked:
                marked = True
                break

        s = new_aut.add_new_state(marked)
        state_map[frozen_states] = s
        notdone_list.append((frozen_states, s))
        return s


    state_map = {}
    notdone_list = []
    states = aut.reachable_states(aut.initial, non_preserved)
    new_aut.set_initial(add_new_state(states, state_map, new_aut, notdone_list))
    while len(notdone_list) > 0:
        states, new_state = notdone_list.pop()

        outgoing_events = set(edge.label for state in states
                                         for edge in state.get_outgoing())

        for evt in preserved.intersection(outgoing_events):
            dest_states = set()
            for state in states:
                for edge in state.get_outgoing(evt):
                    if edge.succ not in dest_states:
                        dest_states.update(aut.reachable_states(edge.succ,
                                                                non_preserved))
                    # else: edge.succ already handled

            if len(dest_states) > 0:
                s2 = add_new_state(dest_states, state_map, new_aut,
                                   notdone_list)
                new_aut.add_edge_data(new_state, s2, evt)

    return new_aut, state_map

# }}} def projection(aut):
# {{{ def inverse_projection(aut):
def inverse_projection(aut):
    """
    Construct a new automaton that is 'complete', at every state, for every
    missing outgoing event, a self loop is added.

    @param aut: Automaton to complete.

    @return: Completed automaton.
    """
    new_aut = aut.copy()

    for state in new_aut.get_states():
        out_events = set(edge.label for edge in state.get_outgoing())
        for evt in new_aut.alphabet.difference(out_events):
            if not evt.observable:
                new_aut.add_edge_data(state, state, evt)

    return new_aut

# }}} def inverse_projection(aut):
# {{{ def complement(aut):
def complement(aut):
    """
    Complement the automaton

    @param aut: Input automaton
    @type  aut: L{Automaton}

    @return: Complement automaton of L{aut}
    @rtype: L{Automaton}
    """
    new_aut = aut.copy()

    # Create dump state
    dump_state = new_aut.add_new_state(marked = True)
    for evt in new_aut.alphabet:
        new_aut.add_edge_data(dump_state, dump_state, evt)

    for state in new_aut.get_states():
        if state is dump_state: # Do not modify dump state
            continue

        # Flip marker state
        flip_single_marker_state(new_aut, state)

        out_events = set(edge.label for edge in state.get_outgoing())
        for evt in new_aut.alphabet.difference(out_events):
            new_aut.add_edge_data(state, dump_state, evt)

    return new_aut

# }}} def complement(aut):

# {{{ def flip_marker_states, flip_single_marker_state
def flip_marker_states(aut):
    """
    Return an automaton that has all marker states flipped

    @param aut: Input automaton
    @type  aut: L{Automaton}

    @return: Flipped automaton of L{aut}
    @rtype: L{Automaton}
    """
    new_aut = aut.copy()

    for state in new_aut.get_states():
        flip_single_marker_state(new_aut, state)

    return new_aut

def flip_single_marker_state(aut, state):
    """
    Flip the 'marked' property of the L{state} in the automaton L{aut}
    """
    marker_event = aut.collection.marker_event
    if marker_event in aut.alphabet:
        marker_edges = list(state.get_outgoing(marker_event))
        if state.marked:
            # State is marked, and marker event in alphabet => check selfloop
            assert len(marker_edges) == 1
            assert marker_edges[0].succ is state
            state.remove_outgoing_edge(marker_edges[0])
        else:
            # Not a marker state -> no self loop (if all is well)
            assert len(marker_edges) == 0 or \
                   (len(marker_edges) == 1 and
                        marker_edges[0].succ is not state)
            aut.add_edge_data(state, state, marker_event)

    # Always flip the state.marker boolean
    state.set_marked(not state.marked)

# }}} def flip_marker_states, flip_single_marker_state

# {{{ def abstract_obervables(plant, sup):
def abstract_obervables(plant, sup):
    """
    Reduce the supervisor to contain only observable transitions between
    states and self loops for non-observable events.

    @param plant: Plant automaton.
    @type  plant: L{Automaton}

    @param sup: Supervisor with observable and non-observable transitions.
    @type  sup: L{Automaton}

    @return: Reduced supervisor.
    @rtype:  L{Automaton}
    """
    prod = product.n_ary_unweighted_product([sup, plant])
    det_prod = unweighted_determinization(prod)
    prod.clear()

    observables = set([evt for evt in det_prod.alphabet
                            if evt.observable or evt.name == 'tau'])
    obs_sup, obsup_map = natural_projection_map(det_prod, observables)

    non_observables = det_prod.alphabet.difference(observables)

    obs_sup.add_event_set(non_observables)

    for det_stateset, obssup_state in obsup_map.iteritems():
        events = set(edge.label for state in det_stateset
                                for edge in state.get_outgoing())

        # Get non-observable events from the set of det-states
        events = events.intersection(non_observables)

        for evt in events:
            obs_sup.add_edge_data(obssup_state, obssup_state, evt)


    obsup_map.clear()
    det_prod.clear() # Used by obsup_map

    return obs_sup

# }}} def abstract_obervables(plant, sup):
