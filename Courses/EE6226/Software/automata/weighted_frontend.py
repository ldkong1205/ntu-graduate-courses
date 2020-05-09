#
# $Id: weighted_frontend.py 726 2010-04-08 10:40:22Z hat $
#
"""
Frontend functions of weighted automata commands.

File format of weighted automata::

    [weighted-automaton]
    initial-state = 0
    states = 0, 1, 2, 3, 4
    alphabet = a, b, c, d
    controllable = a, b
    marker-states = 3, 4
    transitions = (0,1,a,1), (1,2,b,2), (2,0,d,1), (2,3,c,1), (1,4,d,6)

The differences compared to an unweighted automaton are the use of a different
section header, and the addition of a fourth value to each transition, the
weight.

"""
import automata
from automata import abstraction, algorithm, collection, common, \
                     compute_weight, conversion, frontend, product, \
                     supervisor, taskresource, weighted_projection, \
                     weighted_equality, weighted_product, maxplus, \
                     weighted_structure, weighted_supervisor

# {{{ def load_weighted_automaton(collect, fname, test_std, needs_m-states):
def load_weighted_automaton(collect, fname, test_standardized,
                            needs_marker_states):
    """
    Load a weighted automaton file.

    Aborts execution with an error if loading fails in some way.


    @param collect: Collection to store the events of the weighted automaton.
    @type  collect: L{collection.Collection}

    @param fname: Filename of the file to load.
    @type  fname: C{str}

    @param test_standardized: Test whether the loaded automaton is standardized.
    @type  test_standardized: C{bool}

    @param needs_marker_states: Automaton must have at least one marker state.
    @type  needs_marker_states: C{bool}

    @return: Loaded weighted automaton.
    @rtype:  L{Weighted Automaton}
    """
    flags = 0
    if test_standardized:
        flags = flags | frontend.TEST_STANDARDIZED
    if needs_marker_states:
        flags = flags | frontend.MUST_HAVE_MARKER_STATE

    return frontend.load_automaton_file(collect, fname,
                            weighted_structure.WeightedAutomatonLoader, flags)

# }}}
# {{{ def load_weighted_automata(collect, fnames):
def load_weighted_automata(collect, fnames, test_standardized,
                           needs_marker_states):
    """
    Load many automata files.

    Aborts execution with an error if loading fails in some way.


    @param collect: Collection to store the events of the automaton.
    @type  collect: L{collection.Collection}

    @param fnames: Comma-seperated list of automata filenames.
    @type  fnames: C{str}

    @param test_standardized: Test whether the loaded automaton is standardized.
    @type  test_standardized: C{bool}

    @param needs_marker_states: Automaton must have at least one marker state.
    @type  needs_marker_states: C{bool}

    @return: Loaded automata.
    @rtype:  A C{list} of L{WeightedAutomaton}
    """
    aut_list = []
    for fname in fnames.split(','):
        if len(fname) > 0:
            aut_list.append(load_weighted_automaton(collect, fname,
                                        test_standardized, needs_marker_states))

    return aut_list

# }}}
# {{{ def save_weighted_automaton(aut, title, fname):
def save_weighted_automaton(aut, title, fname):
    """
    Save weighted automaton L{aut} in file L{fname}.

    @param aut: Automaton to save.
    @type  aut: L{WeightedAutomaton}

    @param title: If existing, an additional text to output. If it contains
                  C{%s}, string formatting is used to insert the filename at
                  that point in the text.
    @type  title: Either a C{str} or C{None}

    @param fname: Filename to write the automaton to.
    @type  fname: C{str}
    """
    assert isinstance(aut, weighted_structure.WeightedAutomaton)

    frontend.make_backup_file(fname)
    weighted_structure.save_automaton(aut, fname, make_backup = False)

    if title is not None:
        if title.find("%s") >= 0:
            common.print_line(title % (fname,))
        else:
            common.print_line(title)
# }}}
# {{{ def make_weighted_dot(aut_fname, dot_fname)
def make_weighted_dot(aut_fname, dot_fname):
    """
    Convert automaton to Graphviz format.

    @param aut_fname: Filename of the automaton to convert.
    @type  aut_fname: C{str}

    @param dot_fname: Output filename for the Graphviz data.
    @type  dot_fname: C{str}
    """
    coll = collection.Collection()
    aut = load_weighted_automaton(coll, aut_fname, False, False)

    frontend.make_backup_file(dot_fname)

    dot_handle = open(dot_fname, 'w')
    dot_handle.write(aut.to_dot())
    dot_handle.close()

# }}}
# {{{ def make_get_weighted_size(aut_fname)
def make_get_weighted_size(aut_fname):
    """
    Display size of the weighted automaton.

    @param aut_fname: Filename of the weighted automaton.
    @type  aut_fname: C{str}
    """
    common.print_line("Started calculating size (version %s)"
                        % automata.version)
    coll = collection.Collection()
    aut = load_weighted_automaton(coll, aut_fname, False, False)

    print str(aut)

# }}}
# {{{ def make_weighted_product(aut_fnames, result_fname):
def make_weighted_product(aut_fnames, result_fname):
    """
    Multiply the weighthed automata in the L{aut_fnames} list, and write the
    result to L{result_fname}.

    @param aut_fnames: Comma-seperated list of weighted automata filenames.
    @type  aut_fnames: C{str}

    @param result_fname: Filename for writing the resulting weighted automaton.
    @type  result_fname: C{str}
    """
    common.print_line("Started weighted product computations (version %s)"
                        % automata.version)
    coll = collection.Collection()

    aut_list = load_weighted_automata(coll, aut_fnames, False, False)
    result = weighted_product.n_ary_weighted_product(aut_list,
                                                 algorithm.SUM_EDGE_WEIGHTS,
                                                 True, True)

    frontend.dump_stats("Computed product", result)
    save_weighted_automaton(result, "Product is saved in %s\n", result_fname)

# }}}
# {{{ def check_weighted_equality(aut_fname1, aut_fname2):
def check_weighted_equality(aut_fname1, aut_fname2):
    """
    Compare both weighted automata, and return whether they are the same.

    @param aut_fname1: First weighted automaton file to use.
    @type  aut_fname1: C{str}

    @param aut_fname2: Second weighted automaton file to use.
    @type  aut_fname2: C{str}
    """
    common.print_line("Started weigthed equality test (version %s)"
                        % automata.version)
    coll = collection.Collection()

    aut1 = load_weighted_automaton(coll, aut_fname1, False, False)
    aut2 = load_weighted_automaton(coll, aut_fname2, False, False)
    result = weighted_equality.check_weighted_equality(aut1, aut2)

    if result:
        print "weighted equality check: HOLDS"
    else:
        print "weighted equality check: CONFLICT FOUND"

    return result

# }}}
# {{{ def make_remove_weighted(aut_fname, result_fname):
def make_remove_weighted(waut_fname, result_fname):
    """
    Remove the weights of weighted automaton L{waut_fname}, and write the
    result to L{result_fname}.

    @param waut_fname: Filename of weighted automaton to load.
    @type  waut_fname: C{str}

    @param result_fname: Filename of the resulting unweighted automaton.
    @type  result_fname: C{str}
    """
    common.print_line("Started removing weights (version %s)"
                        % automata.version)
    coll = collection.Collection()

    waut = load_weighted_automaton(coll, waut_fname, False, False)
    aut = conversion.remove_weights(waut)

    frontend.save_automaton(aut, "Result is saved in %s\n", result_fname)

# }}}
# {{{ def make_weighted_projection(aut_name, evt_names, result_fname):
def make_weighted_projection(aut_name, evt_names, result_fname):
    """
    Perform projection over a weighted automaton.

    @param aut_name: Filename of the automaton to project.
    @type  aut_name: L{WeightedAutomaton}

    @param evt_names: Comma seperated list of event names to preserve.
    @type  evt_names: C{str}

    @param result_fname: Filename for writing the resulting weighted automaton.
    @type  result_fname: C{str}
    """
    common.print_line("Started weighted projection computation (version %s)"
                        % automata.version)
    coll = collection.Collection()

    waut = load_weighted_automaton(coll, aut_name, False, False)
    events = frontend.get_events(coll, evt_names)

    waut2 = weighted_projection.weighted_projection(waut, events)

    frontend.dump_stats("Computed weighted projection", waut2)
    save_weighted_automaton(waut2, "Projected automaton is saved in %s",
                            result_fname)

# }}} def make_weighted_projection(aut_name, evt_names, result_fname):
# {{{ def make_reset_weighted(aut_fname, result_fname):
def make_reset_weighted(aut_fname, result_fname):
    """
    Reset the weights in weighted automaton L{aut_fname} to 0, and write the
    result to L{result_fname}.

    @param aut_fname: Filename of weighted automaton to load.
    @type  aut_fname: C{str}

    @param result_fname: Filename for writing the resulting weighted automaton.
    @type  result_fname: C{str}
    """
    common.print_line("Started resetting weights (version %s)"
                        % automata.version)
    coll = collection.Collection()

    aut = load_weighted_automaton(coll, aut_fname, False, False)
    aut.reset_weight(0)

    save_weighted_automaton(aut, "Result is saved in %s\n", result_fname)

# }}}

# {{{ make_time_optimal_supervisor(comp_names, req_names, evt_pairs, sup_name)
def make_time_optimal_supervisor(comp_names, req_names, evt_pairs, sup_name):
    """
    Compute a time optimal supervisor.

    @param comp_names: Available components (weighted automata).
    @type  comp_names: C{list} of C{str}

    @param req_names: Available requirements (unweighted automata).
    @type  req_names: C{List} of C{str}

    @param evt_pairs: Additional event pairs (eg "{(a, b), (c, e)}", "type1",
                      or "type2")
    @type  evt_pairs: C{str}

    @param sup_name: Name of resulting supervisor (unweighted automaton).
    @type  sup_name: C{str}
    """
    common.print_line("Started time optimal supervisor computations "
                      "(version %s)" % automata.version)
    coll = collection.Collection()
    comp_list = load_weighted_automata(coll, comp_names, False, True)
    req_list  = frontend.load_automata(coll, req_names, False, True)

    evt_pairs = taskresource.process_event_pairs(coll, req_list, evt_pairs)
    result = compute_weight.compute_time_optimal_supervisor(comp_list,
                                                        req_list, evt_pairs)

    if result is None:
        common.print_line("Time optimal supervisor cannot be computed.")
        return
    else:
        sup, min_weight = result
        common.print_line("Minimum makespan is %d" % min_weight)
        frontend.dump_stats("Computed time optimal supervisor", sup)
        frontend.save_automaton(sup, "Supervisor is saved in %s\n", sup_name)

# }}}

# {{{ def make_optimal_weighted_supervisor(comp_name, req_name, sup_name):
def make_optimal_weighted_supervisor(comp_name, req_name, sup_name):
    """
    Compute a optimal weighted supervisor.

    @param comp_name: Available component (weighted automaton).
    @type  comp_name: C{str}

    @param req_name: Available requirement (unweighted automaton).
    @type  req_name: C{str}

    @param sup_name: Name of resulting supervisor (unweighted automaton).
    @type  sup_name: C{str}
    """
    common.print_line("Started optimal weighted supervisor computation "
                      "(version %s)" % automata.version)
    coll = collection.Collection()
    comp = load_weighted_automaton(coll, comp_name, False, True)
    req  = frontend.load_automaton(coll, req_name,  False, True)

    sup = weighted_supervisor.compute_optimal_weighted_supervisor(comp, req)
    if sup is None:
        common.print_line("Optimal weighted supervisor cannot be computed.")
        return
    else:
        frontend.dump_stats("Computed optimal weighted supervisor", sup)
        frontend.save_automaton(sup, "Supervisor is saved in %s\n", sup_name)

# }}}
# {{{ def make_weighted_supervisor(comp_name, req_name, sup_name):
def make_weighted_supervisor(comp_name, req_name, sup_name):
    """
    Compute a weighted supervisor.

    @param comp_name: Available component (weighted automaton).
    @type  comp_name: C{str}

    @param req_name: Available requirement (unweighted automaton).
    @type  req_name: C{str}

    @param sup_name: Name of resulting supervisor (unweighted automaton).
    @type  sup_name: C{str}
    """
    common.print_line("Started weighted supervisor computation "
                      "(version %s)" % automata.version)
    coll = collection.Collection()
    comp = load_weighted_automaton(coll, comp_name, False, True)
    req  = frontend.load_automaton(coll, req_name,  False, True)

    sup = weighted_supervisor.compute_weighted_supervisor(comp, req)
    if sup is None:
        common.print_line("Weighted supervisor cannot be computed.")
        return
    else:
        frontend.dump_stats("Computed weighted supervisor", sup)
        frontend.save_automaton(sup, "Supervisor is saved in %s\n", sup_name)

# }}}

# {{{ make_greedy_time_optimal_supervisor(comp_names, req_names, evt_pairs):
def make_greedy_time_optimal_supervisor(comp_names, req_names, evt_pairs,
                                        sup_name,L):
    """
    Compute a greedy time optimal supervisor.

    @param comp_names: Available components (weighted automata).
    @type  comp_names: C{list} of L{str}

    @param req_names: Available requirements (unweighted automata).
    @type  req_names: C{list} of L{str}

    @param evt_pairs: Additional event pairs (eg "{(a, b), (c, e)}", "type1",
                      or "type2")
    @type  evt_pairs: C{str}

    @param sup_name: Name of the resulting supervisor.
    @type  sup_name: C{str}
    """
    common.print_line("Started greedy time optimal supervisor "
                      "computation (version %s)" % automata.version)
    coll = collection.Collection()
    comp_list = load_weighted_automata(coll, comp_names, False, True)
    req_list  = frontend.load_automata(coll, req_names, False, True)

    evt_pairs = taskresource.process_event_pairs(coll, req_list, evt_pairs)

    result = taskresource.compute_custom_eventdata(comp_list, evt_pairs)
    if result is None:
        common.print_line('Could not compute the event data from the '
                          'components and event pairs\n'
                          'Perhaps they are inconsistent?')
        return

    eventdata, heap_len = result
    result = compute_weight.compute_greedy_time_optimal_supervisor(
                                                        comp_list, req_list,
                                                        eventdata, heap_len, 0, 0,L)
    if result is None:
        common.print_line('Could not compute the weighted supervisor')
        return

    wsup, wmap = result
    one = maxplus.make_rowmat(0, heap_len)
    one = maxplus.otimes_mat_mat(one, wmap[wsup.initial])
    biggest = one.get_scalar()
    common.print_line("Sub-optimal makespan is %s" % biggest)

    wsup = weighted_supervisor.reduce_automaton(wsup, wmap, eventdata,
                                                heap_len)

    frontend.dump_stats("Computed weighted supervisor", wsup)
    save_weighted_automaton(wsup, "Supervisor is saved in %s\n", sup_name)

# }}}

def make_greedy_time_optimal_supervisor_row_vectors(comp_names, req_names, evt_pairs,
                                        sup_name, row_vectors, operator):
    """
    Compute a greedy time optimal supervisor.

    @param comp_names: Available components (weighted automata).
    @type  comp_names: C{list} of L{str}

    @param req_names: Available requirements (unweighted automata).
    @type  req_names: C{list} of L{str}

    @param evt_pairs: Additional event pairs (eg "{(a, b), (c, e)}", "type1",
                      or "type2")
    @type  evt_pairs: C{str}

    @param sup_name: Name of the resulting supervisor.
    @type  sup_name: C{str}
    """
    common.print_line("Started greedy time optimal supervisor "
                      "computation (version %s)" % automata.version)
    coll = collection.Collection()
    comp_list = load_weighted_automata(coll, comp_names, False, True)
    req_list  = frontend.load_automata(coll, req_names, False, True)

    evt_pairs = taskresource.process_event_pairs(coll, req_list, evt_pairs)

    result = taskresource.compute_custom_eventdata(comp_list, evt_pairs)
    if result is None:
        common.print_line('Could not compute the event data from the '
                          'components and event pairs\n'
                          'Perhaps they are inconsistent?')
        return

    eventdata, heap_len = result
    result = compute_weight.compute_greedy_time_optimal_supervisor(
                                                        comp_list, req_list,
                                                        eventdata, heap_len, row_vectors, operator)
    if result is None:
        common.print_line('Could not compute the weighted supervisor')
        return

    wsup, wmap = result
    one = maxplus.make_rowmat(0, heap_len)
    one = maxplus.otimes_mat_mat(one, wmap[wsup.initial])
    biggest = one.get_scalar()
    common.print_line("Sub-optimal makespan is %s" % biggest)

    wsup = weighted_supervisor.reduce_automaton_row_vecors(wsup, wmap, eventdata,
                                                heap_len, row_vectors)

    frontend.dump_stats("Computed weighted supervisor", wsup)
    save_weighted_automaton(wsup, "Supervisor is saved in %s\n", sup_name)

# }}}


def compute_shortest_path(comp_names, req_names, evt_pairs):
    """
    Compute shortest path with A* algorithm and type 1 requirements.

    @param comp_names: Available components (weighted automata).
    @type  comp_names: C{list} of L{str}

    @param req_names: Name of the requirement automata (unweighted automata).
    @type  req_names: C{list} of L{str}

    @param evt_pairs: Additional event pairs (eg "{(a, b), (c, e)}", "type1",
                      or "type2")
    @type  evt_pairs: C{str}
    """
    common.print_line('Started shortest path type 1 computation (version %s)'
                      % automata.version)
    coll = collection.Collection()
    comp_list = load_weighted_automata(coll, comp_names, False, True)
    req_list  = frontend.load_automata(coll, req_names, False, True)

    evt_pairs = taskresource.process_event_pairs(coll, req_list, evt_pairs)
    compute_weight.compute_shortest_path(comp_list, req_list, evt_pairs)


# {{{ def make_minimal_weighted_supervisor(plant, req, new_fname):
def make_minimal_weighted_supervisor(plant, req, new_fname):
    """
    Compute deterministic weighted supervisor for non-deterministic plant and
    deterministic requirements.

    @param plant: Filename of the non-deterministic weighted (but not
                  minimally) automaton.
    @type  plant: C{str}

    @param req: Filename of the requirements as deterministic non-weighted
                automaton.
    @type  req: C{str}

    @param new_fname: Filename of the created deterministic controller.
    @type  new_fname: C{str}
    """
    common.print_line("Started minimal weighted supervisor computations "
                      "(version %s)" % automata.version)
    coll = collection.Collection()

    plant_waut = load_weighted_automaton(coll, plant, False, True)
    req_aut = frontend.load_automaton(coll, req, False, True)
    wsup = compute_weight.compute_weighted_supremal(plant_waut, req_aut)
    if wsup is None:
        new_aut = None
    else:
        observables = set([evt for evt in plant.events.itervalues()
                           if evt.observable])
        check_marking_aware(wsup, observables)
        wsup2 = weighted_projection.weighted_projection(wsup, observables)
        new_aut = compute_weight.minimal_weight_deterministic_controllable(
                                wsup2)
    if new_aut is None:
        common.print_line("No minimal weight controller found!")

    else:
        unw_plant = conversion.remove_weights(plant_waut)
        prod = product.n_ary_unweighted_product([unw_plant, new_aut[0]])
        result = supervisor.unweighted_determinization(prod)

        common.print_line("Minimum weight is %s" % new_aut[1])
        frontend.save_automaton(result,
                            "Saving minimal weight controller in %s", new_fname)

def check_marking_aware(waut, events):
    """
    Verify that all incoming edges to marker states use events from the
    L{events} set.

    @param waut: Weighted automaton.
    @type  waut: L{WeightedAutomaton}

    @param events: Events that must be used at incoming edges of marker states.
    @type  events: A C{set} of L{Event}
    """
    common.print_line("Started marking aware computations (version %s)"
                        % automata.version)
    warnings = []
    for state in waut.get_states():
        if state.marked:
            labels = set(edge.label for edge in state.get_incoming())
            for evt in labels:
                if evt not in events:
                    warnings.append("\tevent %s to state %d is not observable"
                                    % (evt.name, state.number))
    if len(warnings) > 0:
        common.print_line(["Warning: Plant is not marking aware"])
        common.print_line(warnings)

# }}}

def generate_task_resource_use(comp_names, req_names, text_path, plots,
                               usefname):
    """
    Generate a task/resource usage picture for path L{text_path} with
    components L{comp_names} and requirements L{req_names}. Output data in
    L{usefname}.

    @param comp_names: Available components (weighted automata).
    @type  comp_names: C{list} of L{str}

    @param req_names: Available requirements (unweighted automata).
    @type  req_names: C{list} of L{str}

    @param text_path: Sequence of events on the path (a sequence of event
                      names, comma or white-space seperated).
    @type  text_path: C{string}

    @param plots: Names of automata to plot, if specified.
    @type  plots: C{str}

    @param usefname: Filename for writing task/resource use to.
    @type  usefname: C{str}

    @note: The L{comp_names} and L{req_names} are only used to compute the
           shape of the pieces at the heap. Therefore, for type 1 requirements
           (where the requirements automata are not used in that calculation),
           L{req_names} should be left empty.

    """
    common.print_line('Started generation of task/resource use (version %s)'
                      % automata.version)
    coll = collection.Collection()
    comp_list = load_weighted_automata(coll, comp_names, False, True)
    req_list  = frontend.load_automata(coll, req_names, False, True)

    plots = set(plots.replace(',', ' ').split())
    if plots: # Non-empty set.
        plot_auts = set(aut
                        for aut in comp_list + req_list if aut.name in plots)
    else:
        plot_auts = None # All automata should be plotted.

    uses = compute_weight.generate_task_resource_use(comp_list, req_list,
                                                     plot_auts, text_path)

    if usefname:
        handle = open(usefname, 'w')
        for use in uses:
            handle.write('%s\t%s\t%s\t%s\n' % use)
        handle.close()
    else:
        for use in uses:
            print '%s\t%s\t%s\t%s' % use

def load_unweight_automaton(collect, fname, test_standardized,
                            needs_marker_states):
    """
    Load a weighted automaton file.

    Aborts execution with an error if loading fails in some way.


    @param collect: Collection to store the events of the weighted automaton.
    @type  collect: L{collection.Collection}

    @param fname: Filename of the file to load.
    @type  fname: C{str}

    @param test_standardized: Test whether the loaded automaton is standardized.
    @type  test_standardized: C{bool}

    @param needs_marker_states: Automaton must have at least one marker state.
    @type  needs_marker_states: C{bool}

    @return: Loaded weighted automaton.
    @rtype:  L{Weighted Automaton}
    """
    flags = 0
    if test_standardized:
        flags = flags | frontend.TEST_STANDARDIZED
    if needs_marker_states:
        flags = flags | frontend.MUST_HAVE_MARKER_STATE

    return frontend.load_automaton_file(collect, fname,
                            weighted_structure.WeightedAutomatonLoader, flags)
# }}}

def make_unweight_time_optimal_supervisor(comp_names, req_names, evt_pairs,
                                        sup_name):
    """
    Compute a non weighted time optimal supervisor.

    @param comp_names: Available components (weighted automata).
    @type  comp_names: C{list} of L{str}

    @param req_names: Available requirements (unweighted automata).
    @type  req_names: C{list} of L{str}

    @param evt_pairs: Additional event pairs (eg "{(a, b), (c, e)}", "type1",
                      or "type2")
    @type  evt_pairs: C{str}

    @param sup_name: Name of the resulting supervisor.
    @type  sup_name: C{str}
    """
    common.print_line("Started time unweight optimal supervisor computations "
                      "(version %s)" % automata.version)
    coll = collection.Collection()
    comp_list = load_unweight_automata(coll, comp_names, False, True)
    req_list  = frontend.load_automata(coll, req_names, False, True)
    evt_pairs = taskresource.process_event_pairs(coll, req_list, evt_pairs)

    result = compute_weight.compute_unweight_time_optimal_supervisor(
                                                        comp_list, req_list,
                                                        evt_pairs)
    if result is None:
        common.print_line('Could not compute the weighted supervisor')
        return

    wsup = result
    #one = maxplus.make_rowmat(0, heap_len)
    #one = maxplus.otimes_mat_mat(one, wmap[wsup.initial])
    #biggest = one.get_scalar()
    #common.print_line("Sub-optimal makespan is %s" % biggest)

    #wsup = weighted_supervisor.reduce_automaton(wsup, wmap, eventdata,
    #                                            heap_len)

    frontend.dump_stats("Computed unweighted supervisor", wsup)
    save_weighted_automaton(wsup, "Supervisor is saved in %s\n", sup_name)

# }}}

def load_unweight_automata(collect, fnames, test_standardized,
                           needs_marker_states):
    """
    Load many automata files.

    Aborts execution with an error if loading fails in some way.


    @param collect: Collection to store the events of the automaton.
    @type  collect: L{collection.Collection}

    @param fnames: Comma-seperated list of automata filenames.
    @type  fnames: C{str}

    @param test_standardized: Test whether the loaded automaton is standardized.
    @type  test_standardized: C{bool}

    @param needs_marker_states: Automaton must have at least one marker state.
    @type  needs_marker_states: C{bool}

    @return: Loaded automata.
    @rtype:  A C{list} of L{WeightedAutomaton}
    """
    aut_list = []
    for fname in fnames.split(','):
        if len(fname) > 0:
            aut_list.append(load_unweight_automaton(collect, fname,
                                        test_standardized, needs_marker_states))

    return aut_list

# }}}


def LBE_make_greedy_time_optimal_supervisor(comp_names, req_names, evt_pairs):
    """
    Compute a LBE greedy time optimal supervisor.

    @param comp_names: Available components (weighted automata).
    @type  comp_names: C{list} of L{str}

    @param req_names: Available requirements (unweighted automata).
    @type  req_names: C{list} of L{str}

    @param evt_pairs: Additional event pairs (eg "{(a, b), (c, e)}", "type1",
                      or "type2")
    @type  evt_pairs: C{str}

    @param sup_name: Name of the resulting supervisor.
    @type  sup_name: C{str}
    """
    common.print_line("Started greedy time optimal supervisor "
                      "computation (version %s)" % automata.version)
    coll = collection.Collection()
    comp_list = load_weighted_automata(coll, comp_names, False, True)
    req_list  = frontend.load_automata(coll, req_names, False, True)

    evt_pairs = taskresource.process_event_pairs(coll, req_list, evt_pairs)

    result = taskresource.compute_custom_eventdata(comp_list, evt_pairs)
    if result is None:
        common.print_line('Could not compute the event data from the '
                          'components and event pairs\n'
                          'Perhaps they are inconsistent?')
        return

    eventdata, heap_len = result
    result = compute_weight.LBE_compute_greedy_time_optimal_supervisor(
                                                        comp_list, req_list,
                                                        eventdata, heap_len)
    if result is None:
        common.print_line('Could not compute the weighted supervisor')
        return

    wsup, wmap = result
    one = maxplus.make_rowmat(0, heap_len)
    one = maxplus.otimes_mat_mat(one, wmap[wsup.initial])
    biggest = one.get_scalar()
    common.print_line("Low boundary estimate is %s" % biggest)

# }}}

def load_LBE(LBE_names):

    for fname in LBE_names.split(','):
        if len(fname) > 0:
            header = ''
            linenum = 0
            vocal_states = {}
            trans = []
            name = None
            lbef = 0
            lbes_list = []

            handle = open(fname, 'r')
            for rawline in handle.readlines():
               line = rawline.strip()

               if len(line) > 0:
                   if lbef == 1:
                       lbes_list.append(line)
                   elif line.find("states")!=-1:
                       line   = line.replace('states','')
                       line   = line.replace('=','')
                       states = line.split(',')
                   elif line.find('LBE') !=-1:
                       line        = line.replace('LBE','')
                       line        = line.replace('=','')
                       lbes_list.append(line)
                       lbef        = 1
                   elif line.find('alphabet') != -1:
                       line   = line.replace('alphabet','')
                       line   = line.replace('=','')
                       events = line.split(',')

    if len(states)   <= 0:
          raise exceptions.ModelError('LBE file is not right')
    elif len(lbes_list)  <= 0:
          raise exceptions.ModelError('LBE file is not right')
    elif len(events) <= 0:
          raise exceptions.ModelError('LBE file is not right')

    lbes = []
    for lbe_items in lbes_list:
         lbe_items_list = lbe_items.split('(')
         for lbe_items_tmp in lbe_items_list:
              index = lbe_items_tmp.find(')')
              if index != -1:
                   lbeins = lbe_items_tmp[0:index]
                   lbes.append(lbeins.strip())

    return lbes



def FK_row_vector(comp_names, req_names, evt_pairs):
    """
    Compute a LBE greedy time optimal supervisor.

    @param comp_names: Available components (weighted automata).
    @type  comp_names: C{list} of L{str}

    @param req_names: Available requirements (unweighted automata).
    @type  req_names: C{list} of L{str}

    @param evt_pairs: Additional event pairs (eg "{(a, b), (c, e)}", "type1",
                      or "type2")
    @type  evt_pairs: C{str}

    @param sup_name: Name of the resulting supervisor.
    @type  sup_name: C{str}
    """
    common.print_line("Started greedy time optimal supervisor "
                      "computation (version %s)" % automata.version)
    coll = collection.Collection()
    comp_list = load_weighted_automata(coll, comp_names, False, True)
    req_list  = frontend.load_automata(coll, req_names, False, True)

    evt_pairs = taskresource.process_event_pairs(coll, req_list, evt_pairs)

    result = taskresource.compute_custom_eventdata(comp_list, evt_pairs)
    if result is None:
        common.print_line('Could not compute the event data from the '
                          'components and event pairs\n'
                          'Perhaps they are inconsistent?')
        return

    eventdata, heap_len = result
    result = compute_weight.FK_row_vector(comp_list, req_list, eventdata, heap_len)
    if result is None:
        common.print_line('Could not compute the row vector')
        return









