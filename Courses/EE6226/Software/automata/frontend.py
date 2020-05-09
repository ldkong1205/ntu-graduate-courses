#
# $Id: frontend.py 776 2011-08-15 14:18:21Z hat $
#
"""
Front-end functions
===================

To make the library more easily accessible, wrapper functions have been made
around commonly used functionality.
This file also contains supporting functions for checking file names, etc.

Automaton file format
---------------------
Below an example of an automaton::

    [automaton]
    states = 0, 1, 2, 3, 4, 5
    alphabet = a, b, c, d
    controllable = b
    observable = a, d
    transitions = (0, 1, a), (1, 2, b), (1, 3, d), (2, 4, d), (3, 4, b),
                  (4, 5, c)
    marker-states = 5
    initial-state = 0

By convention, the files have .cfg extension so various editors switch to INI
file format syntax high lighting.

State names may also be an identifier. numbers and names of the form 's<NUM>'
are special in the sense that loading will try to preserve the state numbers.

@todo: Generalize logging messages.
"""
import os, sys, getopt
import automata
from automata import collection, abstraction, supervisor, read_ads, path, \
                     product, verification, common, data_structure, exceptions

DEFAULT_DEVELOPMODE = not automata.installed

# Cmd-line argument processing, input collection/querying
# {{{ def process_inputs(progname, inputs):

EXIST_ADS = 'exist-ads' #: Input must be an existing ADS file.
EXIST_AUT = 'exist-aut' #: Input must be an existing automaton.
EVTLIST = 'event-list'  #: Input is a comma-seperated list of events.
AUT = 'aut'             #: Input is an automaton.
AUTLIST = 'aut-list'    #: Input is a comma-seperated list of automata.
DOT = 'dot'             #: Input is a Graphviz DOT file.
EVTPAIRS = 'evt-pairs'  #: Input is a set of event pairs.
BOOL = "bool"           #: Input is a boolean value.

#: Default input text.
DEFAULTS = {EXIST_ADS : '.ads',
            EXIST_AUT : '.cfg',
            EVTLIST   : "comma-seperated list of event names",
            EVTPAIRS  : '{}',
            AUT       : '.cfg',
            DOT       : '.dot',
            AUTLIST   : 'comma-seperated list of automata',
            BOOL      : 'true'}

class CmdParm(object):
    """
    Description of an command parameter.

    @ivar name: Name of the command parameter.
    @type name: C{str}

    @ivar kind: Type of parameter. Possible values: Keys of L{DEFAULTS}.
    @type kind: C{str}

    @ivar description: Description of the parameter.
    @type description: C{str}

    @ivar value: Value of this parmeter, as given by the user.
    @type value: C{None} if not computed yet, else C{Str}
    """
    def __init__(self, name, kind, accept, description):
        """
        @param name: Name of the command parameter.
        @type  name: C{str}

        @param kind: Type of parameter.
        @type  kind: C{str}

        @param accept: Allowed ways of accepting the parameter value.
        @type  accept: C{str}

        @param description: Description of the parameter.
        @type  description: C{str}

        @note: L{accept} is currently not used.
        """
        self.name = name
        self.kind = kind
        self.description = description
        self.value = None

class Application(object):
    """
    Application base class for a command.

    @ivar parms: Expected inputs of the command.
    @type parms: C{list} of L{CmdParm}

    @ivar cmd: Command being implemented.
    @type cmd: C{str}

    @ivar description: Description of the command.
    @type description: C{str}

    @ivar developmode: Application is running in development mode.
    @type developmode: C{bool}
    """
    def __init__(self, cmd, description):
        self.parms = []
        self.cmd = cmd
        self.description = description
        self.developmode = DEFAULT_DEVELOPMODE

    def add_parm(self, parm):
        """
        Add an command line parameter to the application.

        @param parm: Command line parameter to add.
        @type  parm: L{CmdParm}
        """
        self.parms.append(parm)

    def usage(self, handle):
        """
        Output a help text about using the application.

        @param handle: Output stream to use.
        @type  handle: C{file}
        """
        args, endargs = '', ''
        width = 0
        for cmdparm in self.parms:
            args = args + ' [' + cmdparm.name
            endargs = endargs + ']'

            namelen = len(cmdparm.name)
            if namelen > width:
                width = namelen

        handle.write("%s [options]%s%s\n" % (self.cmd, args, endargs))
        handle.write("with options\n"
                     "    -d, --developmode  Enable development mode\n"
                     "    -h, --help         This help text\n"
                     "    -v, --version      Version information\n"
                     "\n"
                     "with arguments\n")

        for cmdparm in self.parms:
            handle.write("    %-*s %s\n" % (width + 1, cmdparm.name + ':',
                                            cmdparm.description.capitalize()))

        handle.write('\n' + self.description + '\n')

    def run(self):
        """
        Execute the application.

        @return: Exit status, if available.
        @rtype:  C{int} or C{None}
        """
        try:
            self.parms = []
            self.add_options()
            self.process_options()

            args = {}
            for cmdparm in self.parms:
                args[cmdparm.name] = cmdparm.value

            return self.main(args)

        except exceptions.ToolingError, ex:
            print >> sys.stderr, "ERROR: %s" % ex
            if self.developmode:
                raise

            sys.exit(1)

        except SystemExit, ex:
            # Application was already terminated. Note that this exception
            # inherits from L{Exception} prior to Python 2.5, and from
            # L{BaseException} since Python 2.5. For Python versions prior
            # to 2.5, this exception must be before the L{Exception}
            # exception, since otherwise that one applies.
            raise

        except KeyboardInterrupt, ex:
            # Application was forcibly terminated by the user (ctrl+c). Note
            # that this exception inherits from L{Exception} prior to Python
            # 2.5, and from L{BaseException} since Python 2.5. For Python
            # versions prior to 2.5, this exception must be before the
            # L{Exception} exception, since otherwise that one applies.
            print "Application forcibly terminated by the user."
            if self.developmode:
                raise

            sys.exit(1)

        except EOFError, ex:
            # Input stream was closed by the user (ctrl+d). This effectively
            # forcibly terminates the application. Note the newline at the
            # beginning of the message is needed to make sure the message
            # appears on a new line and not on the same line as the request
            # for input.
            print '\nDue to the closure of an input stream by the user, ' \
                  'execution can not continue, and the application will ' \
                  'terminate.'

            if self.developmode:
                raise

            sys.exit(1)

        except Exception, ex:
            # Other/internal error.

            if self.developmode:
                raise

            print >> sys.stderr, "An internal error " + str(ex) + " happened."
            print >> sys.stderr, "Report it, and/or use the '-d' option to " \
                                 "get more information."
            sys.exit(1)


    def process_options(self):
        """
        Do option processing.

        @postcond: The L{CmdParm.value} of all L{self.parms} contains the value
                   given by the user.
        """
        # Command line parsing.
        try:
            opts, args = getopt.getopt(sys.argv[1:], "dhv",
                                            ["developmode", "help", "version"])
        except getopt.GetoptError, err:
            sys.stderr.write(self.cmd + ": " + str(err).capitalize()
                             + ", try '" + self.cmd + " --help'\n")

        # Handle options.
        self.developmode = DEFAULT_DEVELOPMODE

        for opt, val in opts:
            if opt in ('-h', '--help'):
                self.usage(sys.stdout)
                sys.exit(0)

            if opt in ('-v', '--version'):
                if automata.version == '$VERSION':
                    sys.stdout.write("Version: Development version\n")
                else:
                    sys.stdout.write("Version: %s\n" % automata.version)

                sys.exit(0)

            if opt in ('-d', '--developmode'):
                self.developmode = True
                continue

            raise exceptions.ToolingError('Unexpected option %r found'
                                                            % ((opt, val),))

        # Get values from the user
        if len(args) == len(self.parms):
            # We've got all values!
            for cmdparm, arg in zip(self.parms, args):
                cmdparm.value = arg
            return

        elif len(args) > len(self.parms):
            sys.stderr.write("%s: Too many arguments (%d given, %d expected)"
                             "\n" % (self.cmd, len(args), len(self.parms)))
            sys.exit(1)

        else:
            # len(args) < len(inputs), query user
            for idx, cmdparm in enumerate(self.parms):
                if idx < len(args):
                    defval = '"' + args[idx] + '"'
                else:
                    defval = DEFAULTS[cmdparm.kind]
                prompt = 'Please input %s (%s): ' % (cmdparm.description,
                                                     defval)
                while True:
                    text = raw_input(prompt)
                    text = text.strip()
                    if len(text) == 0:
                        if idx < len(args):
                            self.parms[idx].value = args[idx]
                            break
                    else:
                        self.parms[idx].value = text
                        break

            return

    def add_options(self):
        """
        Add command line parameter descriptions to the application.
        """
        pass

    def main(self, args):
        """
        Execute the 'real' functionality.

        @param args: Input for the command line parameters supplied by the
                     user.
        @type  args: C{dict} of C{str} to C{str}

        @return: Exit status, if available.
        @rtype:  C{int} or C{None}
        """
        raise NotImplementedError("Implement me in %s" % str(type(self)))

# }}} Cmd-line argument processing, input collection/querying

# {{{ Load flags
TEST_STANDARDIZED = 0x01 #: Check that the loaded automaton is standardized.
#: Loaded automaton must have one or more marker states.
MUST_HAVE_MARKER_STATE = 0x02
# }}}

# Support functions of automata
# {{{ def load_automaton(collect, fname, test_standardized, needs_marker_states)
def load_automaton(collect, fname, test_standardized, needs_marker_states):
    """
    Load an automaton file.

    Aborts execution with an error if loading fails in some way.


    @param collect: Collection to store the events of the automaton.
    @type  collect: L{collection.Collection}

    @param fname: Filename of the file to load.
    @type  fname: C{str}

    @param test_standardized: Test whether the loaded automaton is standardized.
    @type  test_standardized: C{bool}

    @param needs_marker_states: Automaton must have at least one marker state.
    @type  needs_marker_states: C{bool}

    @return: Loaded automaton.
    @rtype:  L{Automaton}
    """
    flags = 0
    if test_standardized:
        flags = flags | TEST_STANDARDIZED
    if needs_marker_states:
        flags = flags | MUST_HAVE_MARKER_STATE

    return load_automaton_file(collect, fname, data_structure.AutomatonLoader,
                               flags)

def load_automaton_file(collect, fname, loader_class, flags):
    """
    Load an automaton file (generic routine).

    Aborts execution with an error if loading fails in some way.


    @param collect: Collection to store the events of the automaton.
    @type  collect: L{collection.Collection}

    @param fname: Filename of the file to load.
    @type  fname: C{str}

    @param flags: Tests that should be applied after loading.
    @type  flags: C{int}

    @return: Loaded automaton.
    @rtype:  L{Automaton}

    @todo: Check and report event name/property clashes while loading.
    """
    fname = fname.strip()
    if not os.path.isfile(fname):
        raise exceptions.InputError("Automaton file %r does not exist." % fname)

    loader = loader_class(collect)
    aut = loader.load(fname)
    if aut is None:
        raise exceptions.ModelError("Load of file %r failed." % fname)

    if (flags & MUST_HAVE_MARKER_STATE) and len(loader.marker_states) == 0:
        raise exceptions.ModelError("Automaton in file %r has no marker states."
                                                                        % fname)

    if (flags & TEST_STANDARDIZED) and not aut.is_standardized():
        sys.stderr.write("Warning: Automaton %r is not standardized.\n" % fname)
        sys.stderr.write("         Results may be meaningless.\n")

    return aut

# }}}
# {{{ def load_automata(collect, fnames, test_standardized, needs_marker_states)
def load_automata(collect, fnames, test_standardized, needs_marker_states):
    """
    Load many automata files.

    Aborts execution with an error if loading fails in some way.


    @param collect: Collection to store the events of the automaton.
    @type  collect: L{collection.Collection}

    @param fnames: Comma-seperated list of automata filenames.
    @type  fnames: C{str}

    @param test_standardized: Check and report whether the loaded automaton is
                              standardized.
    @type  test_standardized: C{bool}

    @param needs_marker_states: Automaton must have at least one marker state.
    @type  needs_marker_states: C{bool}

    @return: Loaded automata.
    @rtype:  A C{list} of L{Automaton}
    """
    aut_list = []
    for fname in fnames.split(','):
        if len(fname) > 0:
            aut_list.append(load_automaton(collect, fname,
                                       test_standardized, needs_marker_states))

    return aut_list

# }}}
# {{{ def make_backup_file(fname):
def make_backup_file(fname):
    """
    Ensure an existing file L{fname} will not be overwritten by moving it out
    of the way.

    @param fname: Filename to move out of the way.
    @type  fname: C{str}
    """
    if fname == '/dev/null':  # No need to make a backup of /dev/null
        return

    bak_name = fname + ".bak"

    if os.path.exists(fname):
        # Should move the file out of the way

        if os.path.exists(bak_name):
            os.unlink(bak_name)  # Remove previous backup if it exists

        os.rename(fname, bak_name)

# }}}
# {{{ def save_automaton(aut, title, fname):
def save_automaton(aut, title, fname):
    """
    Save automaton L{aut} in file L{fname}.

    @param aut: Automaton to save.
    @type  aut: L{Automaton}

    @param title: If existing, an additional text to output. If it contains
                  C{%s}, string formatting is used to insert the filename at
                  that point in the text.
    @type  title: Either a C{str} or C{None}

    @param fname: Filename to write the automaton to.
    @type  fname: C{str}
    """
    assert isinstance(aut, data_structure.Automaton)

    make_backup_file(fname)
    data_structure.save_automaton(aut, fname, make_backup = False)

    if title is not None:
        if title.find("%s") >= 0:
            common.print_line(title % (fname,))
        else:
            common.print_line(title)

# }}}
# {{{ def dump_stats(title, aut):
def dump_stats(title, aut):
    """
    Output some basic statistics about an automaton.

    @param title: Title to put above the statistics.
    @type  title: C{str}

    @param aut: Automaton.
    @type  aut: L{Automaton}
    """
    common.print_line(title + "\n" + str(aut))
# }}}
def parse_boolean(val):
    val = val.lower()
    if val in ['yes', 'true', '1']:
        return True
    if val in ['no', 'false', '0']:
        return False

    raise exceptions.InputError("%r is not a boolean value." % val)

# Support functions of events
# {{{ def get_events(collect, evt_names):
def get_events(collect, evt_names):
    """
    Retrieve events listed in L{evt_names} from L{collection.Collection}.

    Function aborts if retrieval fails.

    @param collect: Collection to get the events from.
    @type  collect: L{collection.Collection}

    @param evt_names: Comma seperated list of event names.
    @type  evt_names: C{str}

    @return: Events from the collection.
    @rtype:  A C{set} of L{Event}
    """
    events = set()
    for name in evt_names.split(","):
        evt_name = name.strip()
        if evt_name not in collect.events:
            raise exceptions.ModelError("Event '%s' does not exist." % evt_name)
        events.add(collect.events[evt_name])

    return events

# }}}
# {{{ def ensure_tau(collect, events):
def ensure_tau(collect, events):
    """
    Ensure that the C{tau} event exists and is part of L{events}.

    @param collect: Collection to get the events from.
    @type  collect: L{collection.Collection}

    @param events: Events.
    @type  events: A C{set} of L{Event}

    @return: Possibly updated events.
    @rtype:  A C{set} of L{Event}
    """

    if 'tau' not in collect.events:
        raise exceptions.ModelError("Event 'tau' does not exist.")

    tau = collect.events['tau']
    if tau not in events:
        common.print_line("Information: Adding event 'tau' to events.\n")

        evts = events.copy()
        evts.add(tau)
        return evts

    return events

# }}}

# Front-end functions
# {{{ def make_abstraction(aut_name, evt_names, result_fname):
def make_abstraction(aut_name, evt_names, result_fname):
    """
    Perform abstraction of the automaton stored in L{aut_name}, and write the
    result to L{result_fname}.

    @param aut_name: Filename of the automaton to abstract.
    @type  aut_name: L{Automaton}

    @param evt_names: Comma seperated list of event names to preserve.
    @type  evt_names: C{str}

    @param result_fname: Filename for writing the resulting automaton.
    @type  result_fname: C{str}
    """
    common.print_line("Started abstraction computation (version %s)"
                        % automata.version)
    coll = collection.Collection()

    aut = load_automaton(coll, aut_name, True, False)
    events = get_events(coll, evt_names)
    result = abstraction.abstraction(aut, events)

    dump_stats("Computed abstraction", result)
    save_automaton(result, "Abstraction is saved in %s",  result_fname)

# }}}
# {{{ def make_observer_check(aut_name, evt_names):
def make_observer_check(aut_name, evt_names):
    """
    Perform observer_check of the automaton stored in L{aut_name}.

    @param aut_name: Filename of the automaton to abstract.
    @type  aut_name: L{Automaton}

    @param evt_names: Comma seperated list of event names to preserve.
    @type  evt_names: C{str}
    """
    common.print_line("Started observer-check computation (version %s)"
                        % automata.version)
    coll = collection.Collection()

    aut = load_automaton(coll, aut_name, True, False)
    events = get_events(coll, evt_names)
    bad_events = abstraction.observer_check(aut, events)

    if len(bad_events) == 0:
        common.print_line("Observer-check property HOLDS")
    else:
        if len(bad_events) == 1:
            evt_text = "event"
        else:
            evt_text = "events"

        evts = ", ".join(event.name for event in bad_events)
        common.print_line("Observer-check property does not hold "
                          "due to %s %s" % (evt_text, evts))

# }}}
# {{{ def make_minimized(aut_name, result_fname):
def make_minimized(aut_name, result_fname):
    """
    Perform minimization of the automaton stored in L{aut_name}, and write the
    result to L{result_fname}.

    @param aut_name: Filename of the automaton to.
    @type  aut_name: L{Automaton}

    @param result_fname: Filename for writing the resulting automaton.
    @type  result_fname: C{str}
    """
    common.print_line("Started minimization computation (version %s)"
                        % automata.version)
    coll = collection.Collection()

    aut = load_automaton(coll, aut_name, False, False)
    result = abstraction.abstraction(aut, aut.alphabet)

    dump_stats("Computed minimized result", result)
    save_automaton(result, "Minimized automaton is saved in %s",  result_fname)

# }}}
# {{{ def make_controllability_check(plant_fname, sup_fname):

# {{{ def find_disabled_events(sup_aut, plant_aut):
def find_disabled_events(sup_aut, plant_aut):
    """
    Find disabled events in the combined supervisor and plant automata.

    @param sup_aut: Supervisor automaton.
    @type  sup_aut: L{Automaton}

    @param plant_aut: Plant automaton.
    @type  plant_aut: L{Automaton}

    @return: Pair (controlled-disableds, uncontrolled-disableds) with
             controlled-disableds the states with disabled controllable events
             (tuples (sup_state, plant_state, disabled_events)), and
             uncontrolled-disableds the states with disabled uncontrollable
             events (tuple (sup_state, plant_state, disabled_events, sup_path,
             plant_path) with both sup_path and plant_path a tuple (sequence,
             final_state)). The sequence is a number of (state, outgoing event)
             pairs.
    @rtype:  C{tuple} (controlled-disableds, uncontrolled-disableds) with
              - controlled-disableds: a C{list} of (L{State}, L{State}, C{set}
                of L{Event}),
              - uncontrolled-disableds: a C{list} of (L{State}, L{State},
                C{set} of L{Event}, (C{sequence}, L{State}),
                (C{sequence}, L{State})),
                with C{sequence} a C{list} of (L{State}, L{Event}).
    """

    contr_disableds = []
    uncontr_disableds = []

    prod, prod_map = product.n_ary_unweighted_product_map([sup_aut, plant_aut])

    #: Map of prod-state to (sup, plant pair)
    prod_map = product.reverse_statemap(prod_map)

    # For each state in the product, find out what events are disabled.
    # XXX THIS INFORMATION IS KNOWN IN THE N_ARY_PRODUCT!!
    for state in prod.get_states():
        state_events = set(edge.label for edge in state.get_outgoing())

        sup_state, plant_state = prod_map[state]
        plant_events = set(edge.label for edge in plant_state.get_outgoing())

        # Compute disabled events.
        disabled = plant_events.difference(state_events)

        if len(disabled) == 0:
            continue

        # Found disabled events.
        contr_disabled = set([evt for evt in disabled if evt.controllable])
        if len(disabled) == len(contr_disabled):
            # All disabled events are controllable
            contr_disableds.append((sup_state, plant_state, contr_disabled))
        else:
            # At least one uncontrollable event disabled.

            # Perform extended error reporting.

            # Find the path to this state
            seq = path.get_path(prod.initial, state)
            assert seq is not None
            sup_seq = [(prod_map[s][0], e) for s, e in seq
                                           if e in sup_aut.alphabet]
            plant_seq = [(prod_map[s][1], e) for s, e in seq
                                             if e in plant_aut.alphabet]

            uncontr_disableds.append((sup_state, plant_state,
                                     disabled.difference(contr_disabled),
                                     (sup_seq, sup_state),
                                     (plant_seq, plant_state)))

    return contr_disableds, uncontr_disableds
# }}}
# {{{ def make_path_string(seq):
def make_path_string(seq):
    """
    Make a string representation of the sequence.

    @param seq: Sequence to convert.
    @type  seq: Tuple (C{list} of (L{State}, L{Event}), L{State})

    @return: String representation of the sequence.
    @rtype:  C{str}
    """
    elms = ['[%d] -- %s -->' % (s.number, e.name) for s, e in seq[0]] \
            + ['[%d]' % seq[1].number]
    return " ".join(elms)

# }}}

#
# Main function
#
def make_controllability_check(plant_fname, sup_fname):
    """
    Verify whether the plant is controllable with the supervisor.

    @param plant_fname: Filename of the plant automaton.
    @type  plant_fname: C{str}

    @param sup_fname: Filename of the supervisor.
    @type  sup_fname: C{str}
    """
    common.print_line("Started controllability check (version %s)"
                        % automata.version)
    coll = collection.Collection()
    sup_aut = load_automaton(coll, sup_fname, False, False)
    plant_aut = load_automaton(coll, plant_fname, False, False)

    contr_disableds, uncontr_disableds = \
                                find_disabled_events(sup_aut, plant_aut)

    if len(contr_disableds) > 0:
        print "States with disabled controllable events:"
        for sup_s, plant_s, dis_e in contr_disableds:
            print "    (%d, %d): {%s}" % (plant_s.number, sup_s.number,
                                          ", ".join([e.name for e in dis_e]))

        print

    if len(uncontr_disableds) > 0:
        print "States with disabled uncontrollable events:"
        for sup_s, plant_s, dis_e, sup_p, plant_p in uncontr_disableds:
            print "    (%d, %d): {%s}" % (plant_s.number, sup_s.number,
                                          ", ".join([e.name for e in dis_e]))
            print "        Supervisor path: " + make_path_string(sup_p)
            print "        Plant path: " + make_path_string(plant_p)
            print

        print "Supervisor is INCORRECT (has disabled uncontrollable events)"
        sys.exit(1)

    else:
        print "Supervisor is correct (no disabled uncontrollable events)"

# }}}
# {{{ def make_dot(aut_fname, dot_fname)
def make_dot(aut_fname, dot_fname):
    """
    Convert automaton to Graphviz format.

    @param aut_fname: Filename of the automaton to convert.
    @type  aut_fname: C{str}

    @param dot_fname: Output filename for the Graphviz data.
    @type  dot_fname: C{str}
    """
    coll = collection.Collection()
    aut = load_automaton(coll, aut_fname, False, False)

    make_backup_file(dot_fname)

    dot_handle = open(dot_fname, 'w')
    dot_handle.write(aut.to_dot())
    dot_handle.close()

# }}}
# {{{ def convert_from_ads(ads_fname, aut_fname):
def convert_from_ads(ads_fname, aut_fname):
    """
    Convert ADS file to own automaton file format.

    @param ads_fname: Filename of the ADS file to load.
    @type  ads_fname: C{str}

    @param aut_fname: Output filename for the converted automaton.
    @type  aut_fname: C{str}
    """
    coll = collection.Collection()

    aut = read_ads.convert_ads_file(ads_fname, coll)

    dump_stats("Converted automaton", aut)
    save_automaton(aut, "Automaton is saved in %s",  aut_fname)

# }}}
# {{{ def make_get_size(aut_fname)
def make_get_size(aut_fname):
    """
    Display size of the automaton.

    @param aut_fname: Filename of the automaton.
    @type  aut_fname: C{str}
    """
    common.print_line("Started calculating size (version %s)"
                        % automata.version)
    coll = collection.Collection()
    aut = load_automaton(coll, aut_fname, False, False)

    print str(aut)

# }}}
# {{{ def make_add_tau_event(aut_fname, out_fname)
def make_add_tau_event(aut_fname, out_fname):
    """
    Add 'tau' event to the automaton.

    @param aut_fname: Filename of the automaton.
    @type  aut_fname: C{str}

    @param out_fname: Filename of the resulting automaton.
    @type  out_fname: C{str}
    """
    common.print_line("Started adding 'tau' event (version %s)"
                        % automata.version)
    coll = collection.Collection()
    aut = load_automaton(coll, aut_fname, False, False)
    aut = abstraction.add_tau_event(aut)

    dump_stats("Computed result", aut)
    save_automaton(aut, "Result is saved in %s\n", out_fname)

# }}}
# {{{ def make_trim(aut_fname, out_fname)
def make_trim(aut_fname, out_fname):
    """
    Trim the automaton L{aut} (reduce to reachable and co-reachable states).

    @param aut_fname: Filename of the automaton.
    @type  aut_fname: C{str}

    @param out_fname: Filename of the resulting automaton.
    @type  out_fname: C{str}
    """
    common.print_line("Started trimming (version %s)" % automata.version)
    coll = collection.Collection()
    aut = load_automaton(coll, aut_fname, False, False)
    aut.reduce(True, True)

    dump_stats("Computed result", aut)
    save_automaton(aut, "Result is saved in %s\n", out_fname)

# }}}
# {{{ def make_remove_tau_event(aut_fname, out_fname)
def make_remove_tau_event(aut_fname, out_fname):
    """
    Remove 'tau' event from the automaton. May fail.

    @param aut_fname: Filename of the automaton.
    @type  aut_fname: C{str}

    @param out_fname: Filename of the resulting automaton.
    @type  out_fname: C{str}
    """
    common.print_line("Started removing 'tau' event (version %s)"
                        % automata.version)
    coll = collection.Collection()
    aut = load_automaton(coll, aut_fname, False, False)
    abstraction.remove_tau(aut) # Does in-place modification.

    dump_stats("Computed result", aut)
    save_automaton(aut, "Result is saved in %s\n", out_fname)

# }}}
# {{{ def make_natural_projection(aut_name, evt_names, result_fname):
def make_natural_projection(aut_name, evt_names, result_fname):
    """
    Perform projection over a language.

    @param aut_name: Filename of the automaton to project.
    @type  aut_name: L{Automaton}

    @param evt_names: Comma seperated list of event names to preserve.
    @type  evt_names: C{str}

    @param result_fname: Filename for writing the resulting automaton.
    @type  result_fname: C{str}
    """
    common.print_line("Started natural projection computation (version %s)"
                        % automata.version)
    coll = collection.Collection()

    aut = load_automaton(coll, aut_name, False, False)
    events = get_events(coll, evt_names)

    aut2 = supervisor.unweighted_determinization(aut)
    result = supervisor.natural_projection_map(aut2, events)[0]

    dump_stats("Computed projection", result)
    save_automaton(result, "Projected automaton is saved in %s",  result_fname)

# }}} def make_natural_projection(aut_name, evt_names, result_fname):
# {{{ def make_nonconflicting_check(aut_fnames, use_heuristic):
def make_nonconflicting_check(aut_fnames, use_heuristic):
    """
    Verify whether the automata do not conflict with each other.

    @param aut_fnames: Comma-seperated list of automata filenames.
    @type  aut_fnames: C{str}

    @param use_heuristic: Compute a smart order for the automata (rather than
                          use the supplied order).
    @type  use_heuristic: C{str}

    @return: Indication that no conflict has been found (all is ok).
    @rtype:  C{bool}
    """
    common.print_line("Started nonconflicting check (version %s)"
                        % automata.version)
    coll = collection.Collection()
    auts = load_automata(coll, aut_fnames, False, False)

    if parse_boolean(use_heuristic):
        auts = abstraction.order_automata(auts)
    # else, user has supplied the automata in the right order.

    result = abstraction.nonconflicting_check(auts)

    if result:
        print "nonconflicting_check: HOLDS"
    else:
        print "nonconflicting_check: CONFLICT FOUND"

    return result

# }}}
# {{{ def make_product(aut_fnames, result_fname, preserve_names = False):
def make_product(aut_fnames, result_fname, preserve_names = False):
    """
    Multiply the automata in the L{aut_fnames} list, and write the result to
    L{result_fname}.

    @param aut_fnames: Comma-seperated list of automata filenames.
    @type  aut_fnames: C{str}

    @param result_fname: Filename for writing the resulting automaton.
    @type  result_fname: C{str}

    @param preserve_names: Try to preserve state names in the product.
    @type  preserve_names: C{bool}
    """
    common.print_line("Started product computations (version %s)"
                        % automata.version)
    coll = collection.Collection()

    aut_list = load_automata(coll, aut_fnames, False, False)
    result = product.n_ary_unweighted_product(aut_list, True, True,
                                              preserve_names)

    dump_stats("Computed product", result)
    save_automaton(result, "Product is saved in %s\n", result_fname)

# }}}
# {{{ def make_sequential_abstraction(aut_fnames, evt_names, result_fname):
def make_sequential_abstraction(aut_fnames, evt_names, result_fname):
    """
    Perform sequential abstraction on a number of automata.

    @param aut_fnames: Comma-seperated list of automata filenames.
    @type  aut_fnames: C{str}

    @param evt_names: Comma seperated list of event names.
    @type  evt_names: C{str}

    @param result_fname: Filename for writing the resulting automaton.
    @type  result_fname: C{str}
    """
    common.print_line("Started sequential abstraction computations "
                      "(version %s)" % automata.version)
    coll = collection.Collection()

    auts = load_automata(coll, aut_fnames, True, False)
    auts = abstraction.order_automata(auts)

    events = get_events(coll, evt_names)
    events = ensure_tau(coll, events)

    result = abstraction.sequential_abstraction(auts, events)
    save_automaton(result, "Abstraction is saved in %s",  result_fname)

# }}}
# {{{ def make_supervisor(plant_fnames, spec_fname, sup_fname):
def make_supervisor(plant_fnames, spec_fnames, sup_fname):
    """
    Construct a supervisor for controlling a plant within its specification.

    Function aborts if supervisor construction fails.


    @param plant_fnames: Filenames of the plant automata.
    @type  plant_fnames: C{str}

    @param spec_fnames: Filenames of the specification automata.
    @type  spec_fnames: C{str}

    @param sup_fname: Filename for the resulting supervisor.
    @type  sup_fname: C{str}

    @todo: Supervisor computation should set the automaton kind by itself.
    """
    common.print_line("Started supervisor computations (version %s)"
                        % automata.version)
    coll = collection.Collection()

    plants = load_automata(coll, plant_fnames, False, True)
    specs  = load_automata(coll, spec_fnames, False, True)

    sup = supervisor.make_supervisor(plants, specs)
    if sup is None:
        print "Supervisor is empty"
        sys.exit(1)
    else:
        # FIXME: This is the wrong place for setting the result kind
        npl = sum(1 for plant in plants if plant.aut_kind == 'plant')
        nsp = sum(1 for spec in specs   if spec.aut_kind == 'requirement')
        if npl == len(plants) and nsp == len(specs):
            if sup.aut_kind == 'unknown':
                sup.set_kind('supervisor')

        dump_stats("Computed supervisor", sup)
        save_automaton(sup, "Supervisor saved in %s", sup_fname)

# }}}
# {{{ def make_feasible_supervisor(plant_fname, sup_fname, feas_fname):
def make_feasible_supervisor(plant_fname, sup_fname, feas_fname):
    """
    Construct a supervisor containing observable transitions and non-observable
    self-loops.

    @param plant_fname: Filename of the plant automaton.
    @type  plant_fname: C{str}

    @param sup_fname: Filename of the supervisor.
    @type  sup_fname: C{str}

    @param feas_fname: Filename for the resulting supervisor.
    @type  feas_fname: C{str}
    """
    common.print_line("Started feasible supervisor computations (version %s)"
                        % automata.version)
    coll = collection.Collection()

    plant = load_automaton(coll, plant_fname, False, True)
    sup = load_automaton(coll, sup_fname, False, True)

    feas = supervisor.abstract_obervables(plant, sup)
    dump_stats("Computed supervisor", feas)
    save_automaton(feas, "Supervisor saved in %s", feas_fname)

# }}}
# {{{ def make_language_inclusion_test(aut1_fname, aut2_fname):
def make_language_inclusion_test(aut1_fname, aut2_fname):
    """
    Check whether the language of L{aut1_fname} is included in the language of
    L{aut2_fname}.

    @param aut1_fname: Filename of the first automaton (with smallest language).
    @type  aut1_fname: C{str}

    @param aut2_fname: Filename of the second automaton (with biggest language).
    @type  aut2_fname: C{str}
    """
    common.print_line("Started language inclusion test (version %s)"
                        % automata.version)
    coll = collection.Collection()

    aut1 = load_automaton(coll, aut1_fname, False, False)
    aut2 = load_automaton(coll, aut2_fname, False, False)

    res = verification.language_inclusion(aut1, aut2)
    if res:
        print "Language inclusion is CORRECT"
    else:
        print "Language inclusion is INCORRECT"

# }}}

# {{{ def make_language_equivalence_test(aut1_fname, aut2_fname):
def make_language_equivalence_test(aut1_fname, aut2_fname):
    """
    Check whether the language of L{aut1_fname} is included in the language of
    L{aut2_fname}.

    @param aut1_fname: Filename of the first automaton.
    @type  aut1_fname: C{str}

    @param aut2_fname: Filename of the second automaton.
    @type  aut2_fname: C{str}
    """
    common.print_line("Started language equivalence test (version %s)"
                        % automata.version)
    coll = collection.Collection()

    aut1 = load_automaton(coll, aut1_fname, False, False)
    aut2 = load_automaton(coll, aut2_fname, False, False)

    res = verification.language_equivalence(aut1, aut2)
    if res:
        print "Language equivalence HOLDS"
    else:
        print "Language equivalence is INCORRECT"

# }}}


# Other support functions
# {{{ def remove_files(fnames):
def remove_files(fnames):
    """
    Remove every existing file listed in L{fnames}.

    @param fnames: White-space seperated files to remove.
    @type  fnames: C{str}
    """
    for fname in fnames.split():
        if os.path.isfile(fname):
            os.unlink(fname)

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


