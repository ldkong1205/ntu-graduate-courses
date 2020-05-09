#
"""
Data structures for weighted automata.
"""
from automata import data_structure, collection

# {{{ class WeightedEdge(data_structure.Edge):
class WeightedEdge(data_structure.Edge):
    """
    Edge with weight.

    @ivar weight: Weight of the edge.
    @type weight: C{int}
    """
    __slots__ = ['weight']

    def __init__(self, pred, succ, label, weight):
        super(WeightedEdge, self).__init__(pred, succ, label)
        self.weight = weight

    def __repr__(self):
        return "Edge(%r, %r, %r, %r)" % \
                            (self.pred, self.succ, self.label, self.weight)

    def _equals(self, other):
        return self.weight == other.weight and \
               super(WeightedEdge, self)._equals(other)

    def copy(self, new_pred, new_succ):
        """
        Make a copy of the edge, and place it between the given new states.

        @param new_pred: New predecessor state.
        @type  new_pred: L{WeightedState}

        @param new_succ: New successor state.
        @type  new_succ: L{WeightedState}
        """
        return WeightedEdge(new_pred, new_succ, self.label, self.weight)

    def clear(self):
        data_structure.Edge.clear(self)
        self.weight = None

# }}}

#: State in a L{WeightedAutomaton}.
#: @todo: Remove me.
WeightedState = data_structure.BaseState

# {{{ class WeightedAutomaton(data_structure.BaseAutomaton):
class WeightedAutomaton(data_structure.BaseAutomaton):
    """
    Automaton with weighted edges.
    """
    def __init__(self, alphabet, coll):
        super(WeightedAutomaton, self).__init__(alphabet, coll,
                                                WeightedState, WeightedEdge)

    def _make_automaton(self, alphabet):
        return WeightedAutomaton(alphabet, self.collection)

    def add_edge_data(self, pred, succ, label, weight):
        """
        Add an edge from its values.

        @param pred: Source state.
        @type  pred: L{State}

        @param succ: Destination state.
        @param succ: L{State}

        @param label: Event label.
        @type  label: L{Event}

        @param weight: Edge weight.
        @type  weight: C{float}

        @todo: Eliminate me.
        """
        self.add_edge(WeightedEdge(pred, succ, label, weight))

    # {{{ def reset_weight(self, value):
    def reset_weight(self, value):
        """
        Reset the weight of all edges to L{value}.
        """
        for state in self.get_states():
            for edge in state.get_outgoing():
                edge.weight = value
    # }}}
    # {{{ def to_dot(self):
    def to_dot(self):
        """
        Generate a Graphviz DOT representation of the automaton

        @return: String containing the automaton in DOT format
        @rtype:  C{string}
        """
        marker_evt = self.collection.marker_event

        text = ["digraph Automaton {"]
        for state in self.get_states():
            if state is self.initial:
                if marker_evt is not None and state.marked:
                    style = 'doubleoctagon' # initial state with marker event
                else:
                    style = 'octagon'  # initial state without marker event

            elif marker_evt is not None and state.marked:
                style = 'doublecircle'
            else:
                style = 'circle'
            name = 's%d [shape=%s];' % (state.number, style)
            text.append(name)
            for edge in state.get_outgoing():
                text.append("s%s -> s%d [label=\"%s/%d\"];"
                            % (state.number, edge.succ.number,
                               edge.label.name, edge.weight))

        text.append('}')
        return '\n'.join(text)

    # }}}

# }}}

# {{{ Load
class WeightedAutomatonLoader(collection.BaseAutomatonLoader):
    """
    @ivar state_map: Mapping of state name to State.
    @type state_map: C{dict} of C{str} to L{State}
    """
    def __init__(self, coll):
        super(WeightedAutomatonLoader, self).__init__(coll)
        self.state_map = {}


    def make_new_automaton(self, alphabet):
        return WeightedAutomaton(alphabet, self.collection)

    def process_states(self):
        statename_map = self.order_states() #: Mapping of number to name
        self.state_map = {} #: Mapping of name to L{State}
        for num, name in statename_map.iteritems():
            state = self.automaton.add_new_state(name in self.marker_states,
                                                 num = num)
            self.automaton.set_state_name(state, name)
            self.state_map[name] = state

        self.automaton.set_initial(self.state_map[self.initial_state])

    def process_single_edge(self, edge_data):
        if len(edge_data) != 4:
            return "Edge %r should have four fields." % repr(edge_data)

        if not self.is_numeric(edge_data[3]):
            return "Edge weight %r should should be a integer number." % \
                                                            repr(edge_data[3])

        src = self.state_map[edge_data[0]]
        dst = self.state_map[edge_data[1]]
        evt = self.collection.get_event(edge_data[2])
        self.automaton.add_edge_data(src, dst, evt, int(edge_data[3], 10))
        return None

    def get_sectname(self):
        return "weighted-automaton"



def load_automaton(coll, fname):
    """
    Convenience function for loading a weighted automaton.

    @param fname: Name of the file to load.
    @type  fname: C{str}

    @return: Loaded automaton if no errors were found.
    @rtype:  L{WeightedAutomaton}, C{None} if errors were found
    """
    loader = WeightedAutomatonLoader(coll)
    aut = loader.load(fname)
    return aut

# }}}
# {{{ Save
class WeightedAutomatonSaver(collection.BaseAutomatonSaver):
    def check_aut_type(self, aut):
        return type(aut) is WeightedAutomaton

    def get_sectname(self):
        return "weighted-automaton"

    def convert_single_edge(self, aut, edge):
        return "(%s, %s, %s, %s)" % (aut.state_names[edge.pred.number],
                                 aut.state_names[edge.succ.number],
                                 edge.label.name, edge.weight)

def save_automaton(aut, fname, make_backup = True):
    """
    Convenience function for saving a weighted automaton.

    @param fname: Name of the file to load.
    @type  fname: C{str}

    @param aut: Automaton to save.
    @type  aut: L{Automaton}

    @param make_backup: Make a backup file.
    @type  make_backup: C{bool}
    """
    saver = WeightedAutomatonSaver()
    saver.save(aut, fname, make_backup)

# }}}
