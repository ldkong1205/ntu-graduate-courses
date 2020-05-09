#
# $Id: algorithm.py 640 2010-02-01 13:56:44Z hat $
#
"""
Manager classes of the algorithms.
"""
from automata import data_structure, weighted_structure

UNWEIGHTED_AUT = "unweighted_automaton"
WEIGHTED_AUT   = "weighted_automaton"

#: New state is marked if all old states are marked.
MARKED_ALL = "marked_all"
#: New state is marked if one or more old states are marked.
MARKED_ANY = "marked_any"

COMBINED_STATES = "combined_states" #: Return both old and new states as work.
ORIGINAL_STATE = "original_state" #: Only return original state as work.

COPY_LABEL = "copy_label" #: Copy the event label.
FIRST_EDGE = "copy first edge" #: Use the first edge.
MAX_WEIGHT_EDGE = "max_weight_edge" #: Maximal weight of edge.
SUM_EDGE_WEIGHTS = "sum_edge_weights" #: Sum the weights of the edges.
EQUAL_WEIGHT_EDGES = "equal_weight_edges" #: Edges must have equal weights.

# {{{ class ManagerProperties(object):
class ManagerProperties(object):
    """
    Properties used by the manager classes.

    @ivar coll: Collection of the new automaton.
    @type coll: L{Collection}

    @ivar aut_type: Automaton type to create.
    @type aut_type: C{None}, L{UNWEIGHTED_AUT}, or L{WEIGHTED_AUT}

    @ivar alphabet: Alphabet to use for the new automaton.
    @type alphabet: C{set} of L{Event}

    @ivar marker_func: Function to calculate marker property of a state.
    @type marker_func: C{None}, L{MARKED_ALL}, or L{MARKED_ANY}

    @ivar explore_mgr: Sub-manager for keeping track of states to explore.
    @type explore_mgr: C{None}, L{COMBINED_STATES}, or L{ORIGINAL_STATE}

    @ivar edge_calc: Edge calculation helper to use.
    @type edge_calc: C{None}, L{COPY_LABEL}, L{FIRST_EDGE}, L{MAX_WEIGHT_EDGE},
                     L{SUM_EDGE_WEIGHTS}, or L{EQUAL_WEIGHT_EDGES}
    """
    def __init__(self, coll = None):
        """
        Sets up default values for the properties.
        """
        self.coll = coll
        self.aut_type = None
        self.alphabet = None
        self.marker_func = None
        self.explore_mgr = None
        self.edge_calc = None

# }}}

# {{{ class SubManager(object):
class SubManager(object):
    """
    Sub-manager base class.

    @ivar mgr: Main manager.
    @type mgr: L{Manager}
    """
    def __init__(self, mgr):
        self.mgr = mgr

    def setup(self, props):
        """
        Initialize the sub-manager for use.

        @param props: Properties describing what the manager should do.
        @ivar  props: L{ManagerProperties}
        """
        raise NotImplementedError("Implement me in %r" % type(self))

# }}}

# {{{ class AutomatonMaker(SubManager):
class AutomatonMaker(SubManager):
    """
    Class for constructing an automaton, its states, and its edges.

    @ivar aut: Automaton.
    @type aut: L{BaseAutomaton}
    """
    def __init__(self, mgr):
        SubManager.__init__(self, mgr)
        self.aut = None

    def add_state(self, old_state, marked):
        """
        Make a new state that represents the old state.

        @param old_state: Old state.
        @type  old_state: C{collection} of L{BaseState}

        @param marked: Marked property of the new state.
        @type  marked: C{bool}

        @return: New state that represents the old state.
        @rtype:  L{BaseState}
        """
        raise NotImplementedError("Implement me in %r" % type(self))

    def set_initial(self, state):
        """
        Set the initial state of the automaton.

        @param state: State to use as initial state.
        @type  state: L{BaseState}
        """
        raise NotImplementedError("Implement me in %r" % type(self))

    def add_edge(self, edge):
        """
        Add an edge to the automaton.

        @param edge: Edge to add.
        @type  edge: L{Edge}
        """
        raise NotImplementedError("Implement me in %r" % type(self))


class UnweightedAutomatonMaker(AutomatonMaker):
    def setup(self, props):
        self.aut = data_structure.Automaton(props.alphabet, props.coll)

    def add_state(self, old_state, marked):
        return self.aut.add_new_state(marked)

    def set_initial(self, state):
        self.aut.set_initial(state)

    def add_edge(self, edge):
        self.aut.add_edge(edge)

class WeightedAutomatonMaker(AutomatonMaker):
    def setup(self, props):
        self.aut = weighted_structure.WeightedAutomaton(props.alphabet,
                                                        props.coll)

    def add_state(self, old_state, marked):
        return self.aut.add_new_state(marked)

    def set_initial(self, state):
        self.aut.set_initial(state)

    def add_edge(self, edge):
        self.aut.add_edge(edge)

_automaton_makers = {UNWEIGHTED_AUT : UnweightedAutomatonMaker,
                     WEIGHTED_AUT   : WeightedAutomatonMaker,
                     None           : lambda mgr: None,
                    }

# }}}
# {{{ class StateManager(SubManager):
class StateManager(SubManager):
    """
    Class for managing the states used, in particular maintaining the mapping
    from old states to new states.

    @ivar mapping: Mapping of existing old state to new state combinations.
    @type mapping: C{dict} of C{hashable} L{BaseState} to L{BaseState}
    """
    def __init__(self, mgr):
        SubManager.__init__(self, mgr)
        self.mapping = {}

    def setup(self, props):
        pass

    def get_state(self, old_state):
        """
        Return the state representing L{old_state}.

        @param old_state: Existing state.
        @type  old_state: C{iterable} of L{BaseState}

        @return: New state that represents the old state.
        @rtype:  L{BaseState}
        """
        return self.mapping.get(old_state, None)

    def add_mapping(self, old_state, new_state):
        """
        Add new mapping from L{old_state} to L{new_state}.

        @param old_state: Existing state.
        @type  old_state: C{iterable} of L{BaseState}

        @param new_state: State representing the old state.
        @type  old_state: L{BaseState}
        """
        self.mapping[old_state] = new_state

# }}}
# {{{ class MarkerStateComputer(SubManager):
class MarkerStateComputer(SubManager):
    """
    Class for deciding whether an old state represents a marker state.

    @ivar marker_func: Marker state function.
    @type marker_func: L{MARKED_ALL} or L{MARKED_ANY}
    """
    def __init__(self, mgr):
        SubManager.__init__(self, mgr)
        self.marker_func = None

    def setup(self, props):
        self.marker_func = props.marker_func

    def is_marked(self, old_state):
        """
        Decide whether new state should have a marked property.

        @param old_state: Existing state.
        @type  old_state: C{iterable} of L{BaseState}

        @return: Marked property of the new state.
        @rtype:  C{bool}
        """
        if self.marker_func is MARKED_ALL:
            for state in old_state:
                if not state.marked:
                    return False
            return True

        elif self.marker_func is MARKED_ANY:
            for state in old_state:
                if state.marked:
                    return True
            return False

        else:
            raise ValueError("Unsupported marker func %r" % self.marker_func)

# }}}
# {{{ class ExploreManager(SubManager):
class ExploreManager(SubManager):
    """
    Class for managing what states should be explored.

    @ivar not_done: Collection of state combinations that need further
                    exploration.
    @type not_done: C{list} of C{tuple} (C{sequence} L{BaseState},
                    L{BaseState})

    @ivar no_work: Value to return when no work is available.
    @type no_work: constant
    """
    def __init__(self, mgr, no_work):
        SubManager.__init__(self, mgr)
        self.not_done = []
        self.no_work = no_work

    def setup(self, props):
        self.not_done = []

    def add_mapping(self, old_state, new_state):
        """
        A new mapping has been added.

        @param old_state: Existing state.
        @type  old_state: C{iterable} of L{BaseState}

        @param new_state: State representing the old state.
        @type  old_state: L{BaseState}
        """
        raise NotImplementedError("Implement me in %r" % type(self))

    def get_next(self):
        """
        Get next state to explore.

        @return: New state combination to explore if available.
        @rtype:  Depends on sub-class
        """
        if len(self.not_done) == 0:
            return self.no_work

        return self.not_done.pop()

class CombinedStateExplorer(ExploreManager):
    """
    Return the combined old and the new state as item of work.

    @note Not used at all at this moment.
    """
    def __init__(self, mgr):
        ExploreManager.__init__(self, mgr, (None, None))

    def add_mapping(self, old_state, new_state):
        self.not_done.append((old_state, new_state))

class OriginalStateExplorer(ExploreManager):
    """
    Return the old state as item of work.
    """
    def __init__(self, mgr):
        ExploreManager.__init__(self, mgr, None)

    def add_mapping(self, old_state, new_state):
        self.not_done.append(old_state)

_explorers = {COMBINED_STATES : CombinedStateExplorer,
              ORIGINAL_STATE  : OriginalStateExplorer,
              None            : lambda mgr: None,
             }

# }}}
# {{{ class EdgeComputer(SubManager):
class EdgeComputer(SubManager):
    """
    Class for computing new edges.
    """
    def __init__(self, mgr):
        SubManager.__init__(self, mgr)


    def make_edge(self, src, dst, edges):
        """
        Make a new edge from L{src} to L{dst} using the properties of L{edges}.

        @param src: New source state.
        @type  src: L{WeightedState}

        @param dst: New destination state.
        @type  dst: L{WeightedState}

        @param edges: Old edges.
        @type  edges: C{iterable} of L{WeightedEdge}

        @return: New edge.
        @rtype:  L{WeightedEdge}

        @pre:  All edges in L{edges} originate from the old source state, and
               go to the old destination state.
        """
        raise NotImplementedError("Implement me in %r" % type(self))

    def setup(self, props):
        """
        Verify integrity of edge construction w.r.t. used automaton.

        @param props: Properties describing what the manager should do.
        @type  props: L{ManagerProperties}
        """
        if props.edge_calc is FIRST_EDGE:
            pass #: Valid for both automata forms.
        elif props.edge_calc is COPY_LABEL:
            assert props.aut_type is UNWEIGHTED_AUT
        elif props.edge_calc is MAX_WEIGHT_EDGE or \
                props.edge_calc is SUM_EDGE_WEIGHTS or \
                props.edge_calc is EQUAL_WEIGHT_EDGES:
            assert props.aut_type is WEIGHTED_AUT
        else:
            raise ValueError("Edge_calc %r does not match automaton type %r"
                            % (props.edge_calc, props.aut_type))


class CopyLabelEdge(EdgeComputer):
    """
    Make unweighted edge with the same label.
    """
    def make_edge(self, src, dst, edges):
        return data_structure.Edge(src, dst, edges[0].label)

class CopyFirstEdge(EdgeComputer):
    """
    Make edge by copying the first one.
    """
    def make_edge(self, src, dst, edges):
        return edges[0].copy(src, dst)


class MaxWeightEdge(EdgeComputer):
    """
    Make edges with the highest possible weight.
    """
    def make_edge(self, src, dst, edges):
        wght = max(edge.weight for edge in edges)
        return weighted_structure.WeightedEdge(src, dst, edges[0].label, wght)

class SumEdgeWeights(EdgeComputer):
    """
    Sum the weights of the edges.
    """
    def make_edge(self, src, dst, edges):
        wght = sum(edge.weight for edge in edges)
        return weighted_structure.WeightedEdge(src, dst, edges[0].label, wght)

class EqualWeightEdges(EdgeComputer):
    """
    Ensure all weights are the same, and use that value in the new edge.
    """
    def make_edge(self, src, dst, edges):
        wght = edges[0].weight
        if len(edges) > 0:
            for edge in edges:
                assert wght == edge.weight

        return weighted_structure.WeightedEdge(src, dst, edges[0].label, wght)


_edge_computers = {MAX_WEIGHT_EDGE    : MaxWeightEdge,
                   COPY_LABEL         : CopyLabelEdge,
                   FIRST_EDGE         : CopyFirstEdge,
                   SUM_EDGE_WEIGHTS   : SumEdgeWeights,
                   EQUAL_WEIGHT_EDGES : EqualWeightEdges,
                   None               : lambda mgr: None,
                  }

# }}}
# {{{ class Manager(object):
class Manager(object):
    """
    Class for managing the data needed in an algorithm.

    @ivar aut_maker: Sub-manager for making automaton, states, and edges.
    @type aut_maker: L{AutomatonMaker}

    @ivar state_mgr: Sub-manager for managing mapping of old to new states.
    @type state_mgr: L{StateManager}

    @ivar marker_calc: Helper for computing marker state boolean from old
                       states.
    @type marker_calc: L{MarkerStateComputer}

    @ivar explore_mgr: Sub-manager for keeping track of states to explore
                       further.
    @type explore_mgr: L{ExploreManager}

    @ivar edge_calc: Helper for computing new edges.
    @type edge_calc: L{EdgeComputer}
    """
    def __init__(self, props):
        self.aut_maker = None
        self.state_mgr = None
        self.marker_calc = None
        self.explore_mgr = None
        self.edge_calc = None

        self.aut_maker = _automaton_makers[props.aut_type](self)

        # State manager.
        self.state_mgr = StateManager(self)

        if props.marker_func is not None:
            self.marker_calc = MarkerStateComputer(self)

        self.explore_mgr = _explorers[props.explore_mgr](self)
        self.edge_calc = _edge_computers[props.edge_calc](self)


        # Call 'setup' for all sub managers.
        for submgr in [self.aut_maker, self.state_mgr, self.marker_calc,
                       self.explore_mgr, self.edge_calc]:
            if submgr is not None:
                submgr.setup(props)

    def get_state(self, old_state):
        """
        Find or make a new state that represents L{old_state}.

        @param old_state: Old state.
        @type  old_state: C{collection} of L{BaseState}

        @return: New state that represents the old state.
        @rtype:  L{BaseState}
        """
        new_state = self.state_mgr.get_state(old_state)
        if new_state is None:
            if self.aut_maker is not None:
                marked = self.marker_calc.is_marked(old_state)
                new_state = self.aut_maker.add_state(old_state, marked)
            else:
                new_state = None

            self.state_mgr.add_mapping(old_state, new_state)
            self.explore_mgr.add_mapping(old_state, new_state)

        return new_state

    def set_initial(self, old_state):
        """
        Make the given L{old_state} the initial state of the automaton.

        @param old_state: Old state.
        @type  old_state: C{collection} of L{BaseState}

        @return: New state that represents the old state.
        @rtype:  L{BaseState}
        """
        new_state = self.get_state(old_state)
        self.aut_maker.set_initial(new_state)
        return new_state

    def add_edge(self, old_src, old_dst, old_edges):
        """
        Add an edge to the automaton.

        @param old_src: Old source state.
        @type  old_src: C{collection} of L{BaseState}

        @param old_dst: Old destination state.
        @type  old_dst: C{collection} of L{BaseState}

        @param old_edges: Existing edge information. Interpretation depends on
                          L{edge_calc}.
        @type  old_edges: C{collection} of L{Edge} (usually)
        """
        src = self.get_state(old_src)
        dst = self.get_state(old_dst)
        edge = self.edge_calc.make_edge(src, dst, old_edges)
        self.aut_maker.add_edge(edge)

    def get_automaton(self):
        """
        Return the created automaton.

        @return: Automaton created by using the manager.
        @rtype:  L{BaseAutomaton}
        """
        return self.aut_maker.aut

    def get_mapping(self):
        """
        Return the mapping of old states to new states.

        @return: The mapping of old states to new states.
        @rtype:  C{dict} of C{hashable} L{BaseState} to L{BaseState}
        """
        return self.state_mgr.mapping

    def get_next(self):
        """
        Return next state that should be explored.

        @return: Next state to explore.
        @rtype:  Depends on the L{ExploreManager}
        """
        return self.explore_mgr.get_next()

# }}}


class IterativeNodeValueComputation(object):
    """
    Class for iteratively computing a value for each node in an automaton.
    Cycles of updates are used. During a cycle, the L{values} mapping contains
    the values for that cycle. Updates are stored elsewhere, so a consistent
    new state can be computed each cycle.
    L{self.get_nodes()} returns an iterable with nodes (states) that needs
    updating. L{self.update_value()} can be used to update the value of a node
    for the next cycle. If it is different, the change is propagated by marking
    new node(s) for update the next cycle. Which nodes are marked is controlled
    by the L{self.propagate} value given in the constructor.
    Once all nodes of a cycle are re-computed, the next cycle is started with
    L{self.next_cycle()}. If the returned value is C{False}, there are no
    new updates, and L{self.values} contains the final values for all nodes.

    For initialization, typically all nodes get an initial value. To prevent
    that all nodes get marked obsolete, before the first call to
    L{self.next_cycle()}, 'outdated' nodes must be added manually.

    @ivar initing: Is the class data being initialized?
    @type initing: C{bool}

    @ivar propagate: Rule for propagating an update to other nodes. Currently
                     implemented rules:
                      - 'no-propagation': Never propagate changes.
                      - 'backward': Mark predecessors as obsolete.
                      - 'forward':  Mark successors as obsolete.
    @type propagate: C{str}

    @ivar values: Mapping of states in the automaton to values (read-only for
                  the user code).
    @type values: C{dict} of L{BaseState} to anything

    @ivar obsolete_nodes: Collection of 'old' states that should be updated.
    @type obsolete_nodes: C{set} of L{BaseState}

    @ivar next_values: Mapping of states in the automaton to values for the
                       next cycle.
    @type next_values: C{dict} of L{BaseState} to anything

    @ivar next_obsolete_nodes: Collection of 'old' states that should be
                               updated in the next cycle.
    @type next_obsolete_nodes: C{set} of L{BaseState}

    """
    def __init__(self, propagate):
        self.values = {}
        self.obsolete_nodes = set()
        self.next_values = {}
        self.next_obsolete_nodes = set()
        self.initing = True
        self.propagate = propagate

    def get_nodes(self):
        """
        Return an iterable with node that need to be updated in the current
        cycle.

        @return: An iterable with nodes.
        @rtype:  C{iter} of L{BaseState}
        """
        return self.obsolete_nodes

    def next_cycle(self):
        """
        Switch to the next cycle.

        @precond: All nodes marked obsolete in the current cycle have been
        re-computed.

        @return: New cycle is non-empty (that is, we are not yet finished).
        @rtype:  C{bool}
        """
        self.values.update(self.next_values)
        self.obsolete_nodes = self.next_obsolete_nodes

        self.next_values = {}
        self.next_obsolete_nodes = set()
        self.initing = False
        return len(self.obsolete_nodes) != 0

    def update_value(self, node, value):
        """
        Set the value of L{node} to L{value} in the next cycle.
        Also propagate a change for the next cycle.

        @param node: Node to update.
        @type  node: L{BaseState}

        @param value: Value to set.
        @type  value: Anything that is comparable
        """
        self.next_values[node] = value
        if not self.initing:
            if node not in self.values or self.values[node] != value:
                self.propagate_change(node)

    def mark_obsolete(self, node):
        """
        Mark L{node} as obsolete for the next cycle.

        @param node: Node to update.
        @type  node: L{BaseState}
        """
        self.next_obsolete_nodes.add(node)

    def mark_nodes_obsolete(self, nodes):
        """
        Mark all nodes in the iterable as obsolete for the next cycle.
        Convenience method for marking a lot of nodes obsolete.

        @param nodes: Iterable containing nodes to be marked obsolete.
        @type  nodes: C{iter} of L{BaseState}
        """
        for node in nodes:
            self.mark_obsolete(node)

    def propagate_change(self, node):
        """
        L{node} has a new value. Use the propagate rule to mark other nodes as
        obsolete for the next cycle.

        @param node: Updated node.
        @type  node: L{BaseState}
        """
        if self.propagate == 'no-propagation':
            return

        if self.propagate == 'backward':
            for edge in node.get_incoming():
                self.mark_obsolete(edge.pred)
            return

        if self.propagate == 'forward':
            for edge in node.get_outgoing():
                self.mark_obsolete(edge.succ)
            return

        raise ValueError('Unknown propagation rule %r' % self.propagate)

