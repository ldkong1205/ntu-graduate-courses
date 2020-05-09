#
# $Id: taskresource.py 755 2010-12-15 08:21:17Z hat $
#
"""
Tasks and resources.

@todo: Implement a Heap class.
"""
import sys, re
from automata import data_structure, maxplus, weighted_structure, \
                     exceptions

# {{{ def compute_event_duration(auts):
def compute_event_duration(auts):
    """
    Each event label has a fixed duration.

    Find it for all events used in the automata collection, and check
    that it is indeed equal at each edge.

    @param auts: Weighted automata.
    @type  auts: C{list} of L{WeightedAutomaton}

    @return: Mapping of event to its duration if they are consistent,
             C{None} otherwise.
    @rtype:  C{dict} of L{Event} to (C{int} or C{float}), or C{None}
    """
    duration = {}  #: Mapping of event to its duration

    for aut_idx, aut in enumerate(auts):
        for state in aut.get_states():
            for edge in state.get_outgoing():
                length = duration.get(edge.label, None)
                if length is None:
                    duration[edge.label] = edge.weight
                else:
                    if edge.weight != length:
                        sys.stderr.write("Edge '%s' from %s to %s in "
                            "automaton %d has duration %d instead of "
                            "the expected duration %d."
                            % (edge.label.name, state.number,
                               edge.succ.number, aut_idx + 1,
                               edge.weight, length))
                        return None

    return duration

# }}}
# {{{ def compute_eventdata(durations, auts):

class ExtendedEventData(object):
    """
    Helper class that stores data associated with an event.

    @ivar event: Event.
    @type event: L{Event}

    @ivar duration: Duration of the use.
    @type duration: C{int} or C{float}

    @ivar used: Used resources.
    @type used: C{list} of C{bool}

    @ivar matHat: Mr_Hat(evt) matrix.
    @type matHat: L{maxplus.Matrix}
    """
    def __init__(self, event, duration, resources):
        """
        Constructor.

        @param event: Event.
        @type  event: L{Event}

        @param duration: Duration of the use.
        @type  duration: C{int} or C{float}

        @param resources: Available resources (alphabets).
        @type  resources: C{list} of C{set} of L{Event}
        """
        self.event = event
        self.duration = duration
        self.used = [(event in res) for res in resources]

        mat = self._compute_mat(resources, event, duration)
        q_tilde = [self._q_tilde_val(event in res, duration)
                   for res in resources]
        q_check = [self._q_check_val(event in res, duration)
                   for res in resources]
        q_check_mat = maxplus.ColumnMatrix(q_check)
        q_tilde_mat = maxplus.RowMatrix(q_tilde)
        multiply = maxplus.otimes_mat_mat(q_check_mat, q_tilde_mat)
        qq = maxplus.oplus_mat_mat(maxplus.make_unit_matrix(len(resources)),
                                   multiply)
        self.matHat = maxplus.otimes_mat_mat(mat, qq)


    def __str__(self):
        return "\n".join(["Event: %s" % self.event.name,
                          "duration: %s" % self.duration,
                          "resources: %s" % self.used,
                          "matHat: %s" % (self.matHat.dump(),)
                          ])

    def print_self(self):
        """
        Output a human-readable representation of self.
        """
        print str(self)


    def _compute_mat(self, resources, event, duration):
        """
        Compute Mr(a) matrix.

        @param resources: Available resources (alphabets).
        @type  resources: C{list} of C{set} of L{Event}

        @param event: Event.
        @type  event: L{Event}

        @param duration: Duration of the use.
        @type  duration: C{int} or C{float}

        @return: Mr(a) matrix.
        @rtype:  L{maxplus.Matrix}
        """
        mat = maxplus.make_matrix(maxplus.EPSILON,
                                  len(resources), len(resources))
        for ridx, rres in enumerate(resources): # Row iterator
            for cidx, cres in enumerate(resources): # Column iterator
                if ridx == cidx: # Main diagonal
                    if event in rres:
                        mat.set(ridx, cidx, duration)
                    else:
                        mat.set(ridx, cidx, 0)
                else:
                    if event in rres and event in cres:
                        mat.set(ridx, cidx, duration)
                    else:
                        mat.set(ridx, cidx, maxplus.EPSILON)
        return mat

    def _q_tilde_val(self, used, dur):
        """
        Return value to use in Qtilde.

        @param used: Event is used in the resource.
        @type  used: C{bool}

        @param dur: Duration of use.
        @type  dur: C{int} or C{float}

        @return: Max+ value.
        @rtype:  C{int}, C{float}, C{maxplus.EPSILON}, or C{0}
        """
        if used:
            return dur
        return 0

    def _q_check_val(self, used, dur):
        """
        Return value to use in Qcheck.

        @param used: Event is used in the resource.
        @type  used: C{bool}

        @param dur: Duration of use.
        @type  dur: C{int} or C{float}

        @return: Max+ value.
        @rtype:  C{int}, C{float}, C{maxplus.EPSILON}, or C{0}
        """
        if used:
            return -dur
        return maxplus.EPSILON


def compute_eventdata(durations, alphabets):
    """
    Compute for each event the L{ExtendedEventData}.

    @param durations: Mapping of event to its duration.
    @type  durations: C{dict} of L{Event} to (C{int} or C{float})

    @param alphabets: Alphabets to take into account.
    @type  alphabets: C{list} of C{(frozen)set} of L{Event}

    @return: Mapping of events to their event data.
    @rtype:  C{dict} of L{Event} to L{ExtendedEventData}
    """
    return dict((evt, ExtendedEventData(evt, dur, alphabets))
                for evt, dur in durations.iteritems())

# }}}

# {{{ def stack_single_piece(heap, event, eventdata, num_res):
def stack_single_piece(heap, event, eventdata, num_res):
    """
    Stack a single piece at a heap.

    @param heap: Existing heap.
    @type  heap: C{None} for an empty heap, else a L{maxplus.Vector}

    @param event: Event to add.
    @type  event: L{Event}

    @param eventdata: Pieces descriptions.
    @type  eventdata: C{dict} of L{Event} to L{ExtendedEventData}

    @param num_res: Number of resources.
    @type  num_res: C{int}

    @return: Heap with added piece.
    @rtype:  L{maxplus.Vector}
    """
    if heap is None:
        heap = maxplus.make_vector(0, num_res)

    heap = maxplus.otimes_appl(heap, eventdata[event].matHat)
    return heap

# }}}
# {{{ def stack_pieces(events, eventdata, num_res):
def stack_pieces(events, eventdata, num_res):
    """
    Stack pieces onto a heap.

    @param events: Sequence of events to stack.
    @type  events: C{list} of L{Event}

    @param eventdata: Pieces descriptions.
    @type  eventdata: C{dict} of L{Event} to L{ExtendedEventData}

    @param num_res: Number of resources.
    @type  num_res: C{int}

    @return: Heap.
    @rtype:  L{maxplus.Vector}
    """
    heap = None
    for evt in events:
        heap = stack_single_piece(heap, evt, eventdata, num_res)

    return heap

# }}}

HEAP_LESS = "heap_less"
HEAP_EQUAL = "heap_equal"
HEAP_BIGGER = "heap_bigger"
HEAP_UNKNOWN = "heap_unknown"

def compare_heaps(h1, h2):
    """
    Compare two heaps, and return how they compare.

    @param h1: First heap to compare.
    @type  h1: L{maxplus.Vector}

    @param h2: Second heap to compare.
    @type  h2: L{maxplus.Vector}

    @return: Compare result: one of
              - L{HEAP_LESS}: Stacks of L{h1} are <= to those of L{h2}
              - L{HEAP_EQUAL}: L{h1} == L{h2}
              - L{HEAP_BIGGER}: Stacks of L{h1} are >= to those of L{h2}
              - L{HEAP_UNKNOWN}: otherwise.
    @rtype:  C{str}
    """
    assert h1.length() == h2.length()

    less = False #: A stack of h1 is less high than the same stack of h2.
    more = False #: A stack of h2 is less high than the same stack of h1.
    for v1, v2 in zip(h1.data, h2.data):
        less = less or maxplus.lessthan(v1, v2)
        more = more or maxplus.biggerthan(v1, v2)

    if less:
        if more:
            return HEAP_UNKNOWN
        return HEAP_LESS
    else:
        if more:
            return HEAP_BIGGER
        return HEAP_EQUAL

def smallest_add_heap(heaps, heap):
    """
    Add a heap to a collection of smallest heaps.

    @param heaps: Collection of smallest heaps.
    @type  heaps: C{set} of L{maxplus.Vector}

    @param heap: New heap to add.
    @type  heap: L{maxplus.Vector}

    @return: Updated collection of smallest heaps.
    @rtype:  C{set} of L{maxplus.Vector}

    @precond: For all different pairs of heaps in L{heaps},
              L{compare_heaps} must return L{HEAP_UNKNOWN}.
    """
    # Catch some simple cases first.
    if len(heaps) == 0:
        return set([heap])

    if heap in heaps:  # This will catch HEAP_EQUAL
        return heaps

    new_heaps = set()
    for h in heaps:
        result = compare_heaps(h, heap)
        if result == HEAP_UNKNOWN:
            new_heaps.add(h)
            new_heaps.add(heap)
        elif result == HEAP_BIGGER:
            new_heaps.add(heap)
        else:
            assert result == HEAP_LESS
            new_heaps.add(h)

    return new_heaps


def reduce_sup(wsup, weight_map):
    """
    Construct a new automaton containing only edges that lead to a
    decrease in weight.

    @param wsup: Existing automaton.
    @type  wsup: L{WeightedAutomaton}

    @param weight_map: Mapping of states in L{wsup} to their weight.
    @type  weight_map: C{dict} of L{State} to C{int}

    @return: Reduced weighted automaton.
    @rtype:  L{WeightedAutomaton}
    """
    new_aut = weighted_structure.WeightedAutomaton(wsup.alphabet,
                                                   wsup.collection)

    old_initial = wsup.initial
    initial = new_aut.add_new_state(old_initial.marked, old_initial.number)
    new_aut.set_initial(initial)
    notdone = [(old_initial, initial)]

    while len(notdone) > 0:
        old_state, new_state = notdone.pop()
        for edge in old_state.get_outgoing():
            if weight_map[old_state] < weight_map[edge.succ] + edge.weight:
                continue

            if new_aut.has_state(edge.succ.number):
                new_succ = new_aut.get_state(edge.succ.number)
            else:
                new_succ = new_aut.add_new_state(edge.succ.marked,
                                                 edge.succ.number)
                notdone.append((edge.succ, new_succ))
            new_aut.add_edge_data(new_state, new_succ, edge.label, edge.weight)

    return new_aut

def process_event_pairs(coll, req_list, txt):
    """
    Process the text L{txt} describing the event pairs.
    Currently, three forms are understood:
     - "type1"
     - "type2"
     - "{(a, b), .... }"

    @param coll: Collection for retrieving events.
    @type  coll: L{collection.Collection}

    @param req_list: List of requirement automata, needed for handling the
                     'type2' case.
    @type  req_list: C{list} of L{BaseAutomaton}

    @param txt: Text containing the set of pairs of the form "{(e1, e2), ...}"
    @type  txt: C{str}

    @return: Set of event pairs.
    @rtype:  C{set} of C{tuple} of L{Event}

    @note: Tuple combinations are unique, if (e1, e2) is in the result, then
           (e2, e1) is not in the result.
    """
    if txt == 'type1':
        return set()

    if txt == 'type2':
        result = set()
        for aut in req_list:
            result.update(make_ordered_event_pairs(aut.alphabet))
        return result

    return parse_event_pairs(coll, txt)


def make_ordered_event_pairs(alphabet):
    """
    Make an ordered collection of event pairs (ordered in the sense that the
    name of the first field of the pair comes lexicographic before the second
    field).

    @param alphabet: Alphabet to create combinations for.
    @type  alphabet: C{set} of L{Event}

    @return: Set of event pairs.
    @rtype:  C{set} of C{tuple} of L{Event}
    """
    events = sorted(list(alphabet))
    length = len(events)
    return set((events[i], events[j]) for i in range(length - 1)
                                      for j in range(i + 1, length))



def parse_event_pairs(coll, txt):
    """
    Parse a set of (mutual-exclusive) event pairs.

    @param coll: Collection for retrieving events.
    @type  coll: L{collection.Collection}

    @param txt: Text containing the set of pairs of the form "{(e1, e2), ...}"
    @type  txt: C{str}

    @return: Set of event pairs.
    @rtype:  C{set} of C{tuple} of L{Event}

    @note: Tuple combinations are unique, if (e1, e2) is in the result, then
           (e2, e1) is not in the result.
    """
    # Verify that the set is a set (with curly braces around it).
    txt = txt.strip()
    if txt[0] != '{' or txt[-1] != '}':
        msg = "Set of mutual exclusive event pairs has no curly braces " \
              "around the pairs. Please modify the input."
        raise exceptions.InputError(msg)

    pairs = set() #: Collected event pairs

    # Repeatedly match a event tuple.
    pat = re.compile('\\(([^ ,)]*)\\s*,\\s*([^ ,)]*)\\)\\s*,?')
    txt = txt[1:-1]
    while len(txt) > 0:
        m = pat.match(txt)
        if m is None:
            msg = "No event pair found, please verify the input."
            raise exceptions.InputError(msg)

        # Get the events themselves.
        e1 = coll.events.get(m.group(1))
        e2 = coll.events.get(m.group(2))

        # If Event is not available, report an error.
        err_event = None
        if e1 is None:
            err_event = m.group(1)
        if err_event is None and e2 is None:
            err_event = m.group(2)

        if err_event is not None:
            msg = "Event '%s' is not available, please verify the input." \
                  % err_event
            raise exceptions.InputError(msg)

        if (e2, e1) not in pairs:
            pairs.add((e1, e2))

        txt = txt[m.end():].lstrip()

    return pairs

def compute_resources(alphabets, pairs):
    """
    Decide which resources exist.

    Find cliques (a clique is a fully connected graph of events), where each
    alphabet is a clique, and each coupled event pair is also a clique.

    A complete coverage of edges is required, that is each pair should be in a
    resulting clique. In addition, we aim to make each clique as large as
    possible, to reach a normal form.

    @param alphabets: Alphabets of the automata involved.
    @type  alphabets: C{list} of C{set} of L{Event}

    @param pairs: Coupled events.
    @type  pairs: C{set} of C{tuple} of L{Event}

    @return: Resources (sets of cliques covering all edges between events).
    @rtype:  C{set} of C{frozenset} of L{Event}
    """
    # Merge pairs and alphabets.
    for pair in pairs:
        alphabets.append(set(pair))

    #: Map of event to its neighbours (event -> set events).
    neighbours = {}
    for alphabet in alphabets:
        for event in alphabet:
            nb = alphabet.copy()
            nb.remove(event)
            existing_nbs = neighbours.get(event)
            if existing_nbs is None:
                neighbours[event] = nb
            else:
                existing_nbs.update(nb)

    # Remove self-loops.
    for evt, nbs in neighbours.iteritems():
        nbs.discard(evt)


    # Compute the set of cliques to get complete coverage of all edges.

    cliques = set()

    # Add each alphabet to the clique, from large to small so we detect
    # subsets properly.
    alphabets.sort(key=len, reverse = True)
    for alphabet in alphabets:
        # 1. Is alphabet a subset of a clique we already have?
        found = False
        for clique in cliques:
            if alphabet.issubset(clique):
                found = True
                break
        if found:
            continue

        alphabet = alphabet.copy()

        # 2. Try to expand the alphabet.
        # First construct a set of possible neighbours.
        possible_nbs = None
        for evt in alphabet:
            if possible_nbs is None:
                possible_nbs = neighbours[evt]
            else:
                possible_nbs = possible_nbs.intersection(neighbours[evt])
                if len(possible_nbs) == 0:
                    break

        while len(possible_nbs) > 0:
            assert len(possible_nbs.intersection(alphabet)) == 0
            # At least one possible neighbour exists => pick one, and add it.
            evt = possible_nbs.pop()
            alphabet.add(evt)
            possible_nbs = possible_nbs.intersection(neighbours[evt])

        # Add alphabet, should be really new.
        pre_size = len(cliques)
        cliques.add(frozenset(alphabet))
        assert len(cliques) == pre_size + 1

    return cliques

def compute_custom_eventdata(comp_list, evt_pairs):
    """

    @param comp_list: Weighted automata to compute supervisor for.
    @type  comp_list: C{list} of L{WeightedAutomaton}

    @param evt_pairs: Coupled events.
    @type  evt_pairs: C{set} of C{tuple} of L{Event}

    @return: Computed event data and number of resources if it is correct,
             else C{None}.
    @rtype:  C{tuple} of (C{dict} of L{Event} to L{ExtendedEventData},
             C{int}), or C{None}
    """
    # Compute duration of each event (as used in the edges of the automata).
    durations = compute_event_duration(comp_list)
    if durations is None:  # Non-consistent duration found.
        return None

    # Compute ExtendedEventData for each event (max+ matrix and row vectors).
    alphabets = [comp.alphabet for comp in comp_list]
    cliques = compute_resources(alphabets, evt_pairs)
    eventdata = compute_eventdata(durations, cliques)
    return eventdata, len(cliques)


def compute_greedy_eventdata(comp_list, req_list):
    """
    Compute event data for greedy time optimal supervisor.

    @param comp_list: Weighted automata to compute supervisor for.
    @type  comp_list: C{list} of L{WeightedAutomaton}

    @return: Computed event data if it is correct, else C{None}.
    @rtype:  C{dict} of L{Event} to L{ExtendedEventData}, or C{None}
    """
    # Compute duration of each event (as used in the edges of the automata).
    durations = compute_event_duration(comp_list)
    if durations is None:  # Non-consistent duration found.
        return None

    # Compute ExtendedEventData for each event (max+ matrix and row vectors).
    alphabets = [aut.alphabet for aut in comp_list + req_list]
    eventdata = compute_eventdata(durations, alphabets)
    return eventdata

# {{{ def compute_heap_states(unfolded, eventdata, num_res):
def compute_heap_states(unfolded, eventdata, num_res):
    """
    Compute the heap at each state of the tree automaton L{unfolded}.

    @param unfolded: Unweighted tree automaton.
    @type  unfolded: L{Automaton}

    @param eventdata: Pieces descriptions.
    @type  eventdata: C{dict} of L{Event} to L{ExtendedEventData}

    @param num_res: Number of resources.
    @type  num_res: C{int}

    @return: Mapping of states to heap information.
    @rtype:  C{dict} of L{State} to L{maxplus.Vector}
             (initial state uses C{None} to represent empty heap)
    """
    initial_heap = None
    heap_info = {unfolded.initial: initial_heap}
    notdone = [(unfolded.initial, initial_heap)]

    while len(notdone) > 0:
        state, heap = notdone.pop()
        for edge in state.get_outgoing():
            assert edge.succ not in heap_info # A tree automaton has no cycles.
            new_heap = stack_single_piece(heap, edge.label, eventdata, num_res)
            heap_info[edge.succ] = new_heap
            notdone.append((edge.succ, new_heap))

    return heap_info

# }}}

def compute_heap_height(heap):
    """
    Compute the height of L{heap}.

    @param heap: Heap to get maximum height of.
    @type  heap: L{maxplus.Vector}

    @return: Highest point of the heap contour.
    @rtype:  C{int}
    """
    if heap is None: # Empty heap
        return 0

    assert isinstance(heap, maxplus.Vector)
    val = 0
    for hval in heap.data:
        val = maxplus.oplus(val, hval)
    return val


class StackData(object):
    """
    Helper class for storing stack information during pruning.

    @ivar event: Event that brought us to L{state}.
    @type event: L{Event} (C{None} for the initial state)

    @ivar state: State being examined.
    @type state: L{State}

    @ivar unprocessed: Childs to examine:
    @type unprocessed: C{list} of C{tuple} (L{Event}, L{State})

    @ivar minval: Best result found so far.
    @type minval: C{None} or C{int}
    """
    def __init__(self, event, state, unprocessed):
        self.event = event
        self.state = state
        self.unprocessed = unprocessed
        self.minval = maxplus.INFINITE

def prune_tree_automaton(wunfolded, weightmap):
    """
    Reduce the tree automaton L{wunfolded} by pruning away everything except
    the paths to the leafs with the lowest value.

    @param wunfolded: Weighted tree automaton.
    @type  wunfolded: L{WeightedAutomaton}

    @param weightmap: Mapping of weighted states to weight
                      (C{maxplus.INFINITE} for infinite).
    @type  weightmap: C{dict} of L{WeightedState} to C{int}/C{maxplus.INFINITE}

    @return: Pruned tree automaton.
    @rtype:  L{Automaton}

    @note: Weight at the edges is not used.
    """
    coll = wunfolded.collection
    pruned = data_structure.Automaton(wunfolded.alphabet, coll)
    ini_state = wunfolded.initial
    minval = weightmap[ini_state]
    assert minval is not None

    ini_s = pruned.add_new_state(ini_state.marked, ini_state.number)
    pruned.set_initial(ini_s)
    notdone = [ini_state]

    while len(notdone) > 0:
        state = notdone.pop()
        for edge in state.get_outgoing():
            assert weightmap[edge.succ] is not None # Temp paranoia check
            if weightmap[edge.succ] is maxplus.INFINITE:
                continue  # Infinite weight is always bigger than minval

            if weightmap[edge.succ] <= minval:
                nst = pruned.add_new_state(edge.succ.marked, edge.succ.number)
                notdone.append(edge.succ)
                pruned.add_edge_data(pruned.get_state(state.number), nst,
                                     edge.label)
            else:
                assert weightmap[edge.succ] > minval

    return pruned

