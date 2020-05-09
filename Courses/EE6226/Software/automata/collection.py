#
# $Id: collection.py 699 2010-04-06 08:05:44Z hat $
#
"""
Collection of events + automata + weighted automata.
"""
import os, sys, re
from automata import baseobjects, ConfigParser

# {{{ class Collection
class Collection(baseobjects.BaseObject):
    """
    Class to keep the alphabet information, since this is shared between all
    automata of the collection.

    @ivar events: Dictionary of event name to event
    @type events: C{dict} of C{str} to L{Event}

    @ivar marker_event: Event being used to indicate marker state with.
                        A self loop using this event indicates that the state
                        is a marker state.
    @type marker_event: Either C{None} or L{Event}
    """
    def __init__(self):
        baseobjects.BaseObject.__init__(self)
        self.events = {}
        self.marker_event = None
        self.unique_number = 1

        # Create marker event
        self.make_event('marker', True, True, True)

    def clear(self):
        """
        Clear collection.
        """
        self.events = {}
        self.marker_event = None
        self.unique_number = 1

    def make_event(self, name, controllable, observable, marker):
        """
        Add event to the set of available events.

        @return: Added event.
        @rtype:  L{Event}
        """
        evt = Event(name, controllable, observable, marker)
        return self.add_event(evt)

    def add_event(self, evt):
        """
        Add event L{evt}. If an event with the same name already exists
        it must have the same properties or an exception will be raised.

        @return: Added event.
        @rtype:  L{Event}
        """
        if evt.name not in self.events:
            self.events[evt.name] = evt
        else:
            old_evt = self.events[evt.name]
            assert old_evt.controllable == evt.controllable
            assert old_evt.observable == evt.observable
            assert old_evt.marker == evt.marker

        if evt.marker:
            self._set_marker_event(evt)

        return evt

    def _set_marker_event(self, evt):
        """
        Set an event to be used as marker event. Will work exactly once.
        """
        assert self.marker_event is None
        assert evt.name in self.events
        assert evt.name == 'marker'
        assert evt.controllable
        assert evt.observable
        assert evt.marker
        self.marker_event = evt

    def has_event(self, evtname):
        """
        Does the collection have an event named L{evtname}?

        @param evtname: Name of the event to look for.
        @type  evtname: C{str}

        @return: An event with the given name exists.
        @rtype:  C{bool}
        """
        return evtname in self.events

    def get_event(self, evtname):
        """
        Return the event named L{evtname}.

        @param evtname: Name of the event to look for.
        @type  evtname: C{str}

        @return: The requested event.
        @rtype:  L{Event}
        """
        return self.events[evtname]

# }}}
# {{{ class Event
class Event(baseobjects.EqualityObject):
    """
    Class representing an event

    @ivar name: Name of the event
    @type name: C{str}

    @ivar controllable: Is event controllable?
    @type controllable: C{bool}

    @ivar observable: Is event observable?
    @type observable: C{bool}

    @ivar marker: Is event used as marker-state indication?
    @type marker: C{bool}
    """
    def __init__(self, name, controllable, observable, marker):
        baseobjects.EqualityObject.__init__(self)
        self.name = name
        self.controllable = controllable
        self.observable = observable
        self.marker = marker

        if self.marker:
            assert self.controllable
            assert self.observable

    def _equals(self, other):
        equal = self.name == other.name
        if equal:
            assert self.controllable == other.controllable
            assert self.observable == other.observable
            assert self.marker == other.marker

        return equal

    def __cmp__(self, other):
        if type(self) is not type(other):
            return cmp(type(self), type(other))
        if self.name != other.name:
            return cmp(self.name, other.name)
        # Equal names implies equal properties
        assert self.controllable == other.controllable
        assert self.observable == other.observable
        assert self.marker == other.marker
        return 0

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return "Event(%r, ctrl=%s, obs=%s, marker=%s)" \
               % (self.name, self.controllable, self.observable, self.marker)

# }}}

# {{{ class BaseAutomatonLoader(object):
class MyConfigParser(ConfigParser.ConfigParser):
    """ Derived ConfigParser class without name-mangling behavior """
    def optionxform(self, name):
        """ Conversion of name is identity function """
        return str(name)

class BaseAutomatonLoader(object):
    """
    Automa loader class, providing specific details for the generic loader.

    @ivar collection: Collection to use for the events.
    @type collection: L{Collection}

    @ivar raw_data: Raw data of the automaton file.
    @type raw_data: C{dict} of otions C{str} to values C{str}


    @ivar aut_kind: Kind of automaton. Currently known values: C{'plant'},
                    C{'requirement'}, C{'supervisor'}, and C{'unknown'}.
    @type aut_kind: C{str}

    @ivar alphabet: Alphabet of the loaded automaton.
    @type alphabet: C{set} of C{str}

    @ivar observable_events: Obervable events subset.
    @type observable_events: C{set} of C{str}

    @ivar controllable_events: Controllable events subset.
    @type controllable_events: C{set} of C{str}

    @ivar marker_events: Marker events subset.
    @type marker_events: C{set} of C{str}


    @ivar states: States of the automaton.
    @type states: C{set} of C{str}

    @ivar initial_state: Name of the initial state, if defined.
    @type initial_state: C{str} or C{None}

    @ivar marker_states: Marker states of the automaton.
    @type marker_states: C{set} of C{str}


    @ivar automaton: Automaton to return to the user, if available.
    @type automaton: L{Automaton}
    """
    def __init__(self, coll):
        self.collection = coll
        self.raw_data = {}
        self.aut_kind = 'unknown'
        self.alphabet = set()
        self.observable_events = set()
        self.controllable_events = set()
        self.marker_events = set()
        self.states = set()
        self.initial_state = None
        self.marker_states = set()
        self.automaton = None

        assert isinstance(self.collection, Collection)

    def load(self, fname):
        """
        Load the automaton file name L{fname} into the collection.
        Note that the events defined by the loaded automaton must match with
        the already existing events.

        @param fname: Name of the file to load.
        @type  fname: C{str}

        @return: Loaded automaton if no errors were found.
        @rtype:  L{Automaton}, C{None} if errors were found
        """
        result = self._load_data(fname)
        if result is not None:
            sys.stderr.write(result + "\n")
            return None

        # Set the name of the automaton
        basename = os.path.basename(fname)
        if len(basename) > 4 and basename.lower()[-4:] == '.cfg':
            basename = basename[:-4]
        self.automaton.set_name(basename)

        return self.automaton

    # {{{ def _load_data(self, fname):
    def _load_data(self, fname):
        """
        Load the automaton file name L{fname} into the collection.
        Note that the events defined by the loaded automaton must match with
        the already existing events.

        @param fname: Name of the file to load.
        @type  fname: C{str}

        @return: Loaded automaton
        @rtype:  L{Automaton}
        """
        # Load raw data.
        cfg = MyConfigParser()
        cfg.read(fname)
        errtxt = self.get_section_data(cfg)
        if errtxt is not None:
            return errtxt

        # Load automaton kind.
        errtxt = self.load_automaton_kind()
        if errtxt is not None:
            return errtxt

        # Load events.
        errtxt = self.load_events()
        if errtxt is not None:
            return errtxt

        errtxt = self.process_events_kind()
        if errtxt is not None:
            return errtxt

        # Load states.
        errtxt = self.load_states()
        if errtxt is not None:
            return errtxt

        errtxt = self.process_states()
        if errtxt is not None:
            return errtxt

        # Load edges.
        if 'transitions' not in self.raw_data:
            return "Missing 'transitions' field in data file."

        for match in re.finditer('\\([^()]+\\)', self.raw_data['transitions']):
            edge_text = match.group(0)
            edge_data = self._get_identifiers(edge_text[1:-1])
            if len(edge_data) < 3:
                return "Edge %r does not have at least three fields." % \
                                                                    edge_text

            if edge_data[0] not in self.states:
                return ("Edge %r has an invalid source state %r."
                        % (edge_text, edge_data[0]))

            if edge_data[1] not in self.states:
                return ("Edge %r has an invalid destination state %r."
                        % (edge_text, edge_data[1]))

            if edge_data[2] not in self.alphabet:
                return ("Edge %r has an invalid event %r."
                        % (edge_text, edge_data[2]))

            errtxt = self.process_single_edge(edge_data)
            if errtxt is not None:
                return errtxt

        return None

    # }}}
    # {{{ def process_events_kind(self):
    def process_events_kind(self):
        """
        Copy events to the automaton.

        @return: Result of loading states.
        @rtype:  If an error was found, a string describing the problem is
                 returned. If no error was found, C{None} is returned.
        """
        alphabet = set() #: Alphabet as a set of L{Event}
        for evtname in self.alphabet:
            if self.collection.has_event(evtname):
                event = self.collection.get_event(evtname)
                if event.controllable != (evtname in self.controllable_events):
                    return "Controllability property of event %s is not " \
                           "correct." % evtname
                if event.observable != (evtname in self.observable_events):
                    return "Observability property of event %s is not " \
                           "correct." % evtname
                if event.marker != (evtname in self.marker_events):
                    return "Marker property of event %s is not " \
                           "correct." % evtname
            else:
                event = self.collection.make_event(evtname,
                                        evtname in self.controllable_events,
                                        evtname in self.observable_events,
                                        evtname in self.marker_events)

            alphabet.add(event)

        self.automaton = self.make_new_automaton(alphabet)
        self.automaton.set_kind(self.aut_kind)
        return None

    def make_new_automaton(self, alphabet):
        """
        Construct a new automaton.
        """
        raise NotImplementedError("Implement me in a derived class.")

    # }}}
    # {{{ def process_states(self):
    def is_numeric(self, name):
        """
        Decide whether L{name} is numeric (contains only digits).

        @param name: Name to investigate.
        @type  name: C{str}

        @return: Name contains (ASCII) digits only.
        @rtype:  C{bool}
        """
        if len(name) == 0:
            return False

        for kar in name:
            if kar < '0' or kar > '9':
                return False
        return True

    def order_states(self):
        """
        Try to be smart about assigning numeric values to state names.

        @return: Mapping of numbers to state names, may contain gaps.
        @rtype:  C{dict} of C{int} to C{str}
        """
        state_map = {}
        identifier_states = []
        biggest_num = 0
        # 1. Convert pure numeric states.
        remaining = []
        for name in self.states:
            if self.is_numeric(name):
                numval = int(name, 10)
                if numval not in state_map:
                    state_map[numval] = name
                    biggest_num = max(biggest_num, numval)
                else:
                    identifier_states.append(name) # number used twice
            else:
                remaining.append(name)

        # 2. Convert almost numeric states.
        for name in remaining:
            if self.is_numeric(name[1:]):
                numval = int(name[1:], 10)
                if numval not in state_map:
                    state_map[numval] = name
                    biggest_num = max(biggest_num, numval)
                    continue

            identifier_states.append(name)

        # 3. Convert other states.
        for name in identifier_states:
            biggest_num = biggest_num + 1
            state_map[biggest_num] = name

        return state_map

    def process_states(self):
        """
        Copy loaded states to the automaton."
        """
        raise NotImplementedError("Implement me in a derived class.")

    # }}} def process_states(self):
    # {{{ def get_section_data(self, cfg):
    def get_section_data(self, cfg):
        """
        Get the contents of the section to load.

        @param cfg: Configuration data.
        @type  cfg: L{MyConfigParser}

        @postcond: L{raw_data} contains the raw data from the config file.

        @return: Error message.
        @rtype:  C{str} if loading failed, C{None} if loading succeeded.
        """
        sectname = self.get_sectname()
        if not cfg.has_section(sectname):
            return "Could not find a section [%s]." % sectname

        self.raw_data = dict(cfg.items(sectname))
        return None

    def get_sectname(self):
        """
        Return the name of the section to read from the cfg file.
        """
        raise NotImplementedError("Implement me in a derived class.")

    # }}} def get_section_data(self, cfg):
    # {{{ def load_automaton_kind(self):
    def load_automaton_kind(self):
        """
        Load the application kind of the automaton.

        @postcond: Upon success of the method, L{aut_kind} contains the
                   kind of the loaded automaton.

        @return: Result of loading events.
        @rtype:  If an error was found, a string describing the problem is
                 returned. If no error was found, C{None} is returned.
        """
        self.aut_kind = self.raw_data.get('kind', 'unknown')
        return None
    # }}} def load_automaton_kind(self):
    # {{{ def load_events(self):
    def load_events(self):
        """
        Load the events of the file data into the loader variables.

        @postcond: Upon success of the method, L{alphabet} contains the
                   alphabet of the loaded automaton.

        @postcond: Upon success of the method, L{observable_events} contains
                   the observable subset of the alphabet of the loaded
                   automaton.

        @postcond: Upon success of the method, L{controllable_events} contains
                   the controllable subset of the alphabet of the loaded
                   automaton.

        @return: Result of loading events.
        @rtype:  If an error was found, a string describing the problem is
                 returned. If no error was found, C{None} is returned.

        @todo: Remove marker events?
        """
        # Alphabet loading.
        if 'alphabet' not in self.raw_data:
            return "Field 'alphabet' not in data file."

        self.alphabet = set(self._get_identifiers(self.raw_data['alphabet']))

        self.observable_events, res = self.load_event_subset('observable')
        if res is not None:
            return res

        self.controllable_events, res = self.load_event_subset('controllable')
        if res is not None:
            return res

        self.marker_events, res = self.load_event_subset('marker')
        if res is not None:
            return res

        return None

    def load_event_subset(self, name):
        """
        Load an optional subset of events from the file data.

        @param name: Name of the subset (in the file data).
        @type  name: C{str}

        @return: Loaded subset (in case no error occurred) and an error result.
        @rtype:  C{tuple} (C{set} of C{str}, (C{str} or C{None}

        @precond: L{alphabet} must be initialized.
        """
        if name in self.raw_data:
            subset = set(self._get_identifiers(self.raw_data[name]))
        else:
            subset = set()

        result = None
        unknowns = subset.difference(self.alphabet)
        if len(unknowns) == 1:
            result = name.capitalize() + (" event %r is not in the alphabet." %
                                                                unknowns.pop())
        elif len(unknowns) > 1:
            result = name.capitalize() + (" events %s are not in the alphabet." %
                            ", ".join([repr(unknown) for unknown in unknowns]))

        return subset, result

    # }}} def load_events(self):
    # {{{ def load_states(self):
    def load_states(self):
        """
        Load states from the file data.

        @return: Result of loading states.
        @rtype:  If an error was found, a string describing the problem is
                 returned. If no error was found, C{None} is returned.
        """
        if 'states' not in self.raw_data:
            return "Field 'states' not in data file."

        self.states = set(self._get_identifiers(self.raw_data['states']))

        if 'initial-state' not in self.raw_data:
            return "Field 'initial-state' not in data file."

        self.initial_state = self.raw_data['initial-state'].strip()
        if self.initial_state not in self.states:
            return "Initial state is not in the state set."

        result = None
        if 'marker-states' in self.raw_data:
            self.marker_states = set(self._get_identifiers(
                                                self.raw_data['marker-states']))
            unknowns = self.marker_states.difference(self.states)
            if len(unknowns) == 1:
                result = "Marker state %r is not in the alphabet." % \
                                                                unknowns.pop()
            elif len(unknowns) > 1:
                result = "Marker states %s are not in the alphabet." % \
                            ", ".join([repr(unknown) for unknown in unknowns])

        else:
            self.marker_states = set()

        return result

    # }}} def load_states(self):
    def process_single_edge(self, edge_data):
        """
        Add an edge to the automaton.

        @param edge_data: Edge data. First three fields are src-state,
                          dest-state, event.
        @type  edge_data: C{tuple} of C{str}
        """
        raise NotImplementedError("Implement me in a derived class.")

    # {{{ def _get_identifiers(self, text):
    def _get_identifiers(self, text):
        """
        Extract the identifiers from L{text}, dropping comma's and white space.

        @param text: Text to extract identifiers from.
        @type  text: C{str}

        @return: Identifiers fround in the L{text}.
        @rtype:  C{list} of C{str}
        """
        idens = []
        idx = 0
        while idx < len(text):
            # Skip white-space.
            while idx < len(text) and text[idx] in ' \n\t\r,':
                idx = idx + 1

            if idx >= len(text):
                break

            end = idx + 1
            while end < len(text) and text[end] not in ' \n\t\r,':
                end = end + 1

            idens.append(text[idx:end])
            idx = end + 1

        return idens

    # }}} def _get_identifiers(self, text):

# }}}
# {{{ class BaseAutomatonSaver(object):
class BaseAutomatonSaver(object):
    """
    Base class for saving an automaton.

    @ivar cfg: Data to store.
    @type cfg: C{None} if no data to store, else L{ConfigParser}
    """
    def __init__(self):
        super(BaseAutomatonSaver, self).__init__()
        self.cfg = None

    def save(self, aut, fname, make_backup = True):
        """
        Save L{aut} to file with name L{fname}.

        @param aut: Automaton to save.
        @type  aut: L{BaseAutomaton}

        @param fname: Filename to save the automaton to, '-' means stdout.
        @type  fname: C{str}

        @param make_backup: Make a backup file.
        @type  make_backup: C{bool}
        """
        self.cfg = ConfigParser.ConfigParser()
        self.cfg.add_section(self.get_sectname())

        result = self._store(aut)
        if result is not None:
            sys.stderr.write('Save failed: ' + result + '\n')
            return

        # Make backup.
        if fname != '-' and make_backup and os.path.isfile(fname):
            if os.path.isfile(fname + ".bak"):
                os.unlink(fname + ".bak")
            os.rename(fname, fname + ".bak")

        # Save the data.
        if fname == '-':
            self.cfg.write(sys.stdout)
        else:
            handle = open(fname, "w")
            self.cfg.write(handle)
            handle.close()


    def _store(self, aut):
        """
        Store L{aut} in L{cfg}.

        @param aut: Automaton to save.
        @type  aut: L{BaseAutomaton}

        @return: Result of the store.
        @rtype:  C{str} if an error, C{None} otherwise
        """
        if aut.initial is None: # Refuse to save an empty automaton.
            return "Automaton is empty."

        result = self.check_aut_type(aut)
        if not result:
            return "Wrong type of automaton."

        # Write kind.
        self.cfg.set(self.get_sectname(), 'kind', aut.aut_kind)

        # Write events.
        evtnames = [evt.name for evt in aut.alphabet]
        evtnames.sort()
        self.cfg.set(self.get_sectname(), 'alphabet', ", ".join(evtnames))

        evtnames = [evt.name for evt in aut.alphabet if evt.controllable]
        if len(evtnames) > 0:
            evtnames.sort()
            self.cfg.set(self.get_sectname(), 'controllable',
                                                            ", ".join(evtnames))

        evtnames = [evt.name for evt in aut.alphabet if evt.observable]
        if len(evtnames) > 0:
            evtnames.sort()
            self.cfg.set(self.get_sectname(), 'observable', ", ".join(evtnames))

        evtnames = [evt.name for evt in aut.alphabet if evt.marker]
        if len(evtnames) > 0:
            evtnames.sort()
            self.cfg.set(self.get_sectname(), 'marker', ", ".join(evtnames))

        # Write states.
        aut.make_state_names_complete()

        statenames = [aut.state_names[state.number]
                                                for state in aut.get_states()]
        statenames.sort()
        self.cfg.set(self.get_sectname(), 'states', ", ".join(statenames))

        self.cfg.set(self.get_sectname(), 'initial-state',
                                            aut.state_names[aut.initial.number])

        statenames = [aut.state_names[state.number]
                                for state in aut.get_states() if state.marked]
        statenames.sort()
        self.cfg.set(self.get_sectname(), 'marker-states',
                                                    ", ".join(statenames))

        # Write transitions.
        lines = []
        line = ''
        states = [(state.number, state) for state in aut.get_states()]
        states.sort()
        for _number, state in states:
            edges = [(edge.succ.number, edge.label, edge)
                     for edge in state.get_outgoing()]
            edges.sort()
            for _succ, _label, edge in edges:
                txt = self.convert_single_edge(aut, edge)
                if line == '':
                    line = txt  # First time only.
                else:
                    if len(line) > 70:
                        lines.append(line + ',')
                        line = txt
                    else:
                        line = line + ", " + txt
        if line != '':
            lines.append(line)

        transs = "\n    ".join(lines)
        self.cfg.set(self.get_sectname(), 'transitions', transs)
        return None


    def check_aut_type(self, aut):
        """
        Check that the automaton can be saved by this saver class.

        @param aut: Automaton to save.
        @type  aut: L{BaseAutomaton}

        @return: The automaton can be saved.
        @rtype:  C{bool}
        """
        raise NotImplementedError("Implement me in a derived class.")

    def get_sectname(self):
        """
        Return the name of the section to read from the cfg file.
        """
        raise NotImplementedError("Implement me in a derived class.")

    def convert_single_edge(self, aut, edge):
        """
        Convert edge L{edge} in automaton L{aut} to text.

        @param aut: Automaton to save.
        @type  aut: L{BaseAutomaton}

        @param edge: Edge to convert.
        @type  edge: L{Edge}
        """
        raise NotImplementedError("Implement me in a derived class.")

# }}}
