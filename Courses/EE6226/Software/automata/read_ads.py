#
# $Id: read_ads.py 620 2010-01-25 13:54:15Z hat $
#

from automata import data_structure, exceptions

def read_ads_file(fhandle):
    """
    Load an ADS file, and return its data.

    @param fhandle: File handle of the ADS file.
    @type  fhandle: C{file}

    @return: The data of the ADS file,
             (name, n_state_size, marker_lines, vocal_states, trans)
    @rtype:  (C{str}, C{int}, either C{['*']} or a list of integers,
             C{dict} of C{int}-state to C{int}-event, list of (C{int}-srcstate,
             C{int}-event, C{int}-deststate))

    @note: States are numbered from C{0} (initial state) upto C{n_state_size-1}.
           Odd event numbers are considered to be controllable.
           Even event numbers are considered to be uncontrollable.
           C{['*']} for marker states means all states are marker state.

    @note: Code written by J.Hamer, edited by A.T.Hofkamp.
    @note: Copied from svctools/trunk/svctools/bin/ads2stm r368 (21-04-2009).
    """

    header = ''
    linenum = 0
    vocal_states = {}
    marker_lines = []
    trans = []
    name = None

    for rawline in fhandle.readlines():
        line = rawline.strip()
        linenum = linenum + 1
        if line == '':
            header = ''
        elif line[0] == '#':
            pass
        elif line == 'State size (State set will be (0,1....,size-1)):':
            header = 'Size'
        elif line == 'Marker states:':
            header = 'Marker'
        elif line == 'Vocal states:':
            header = 'Vocal'
        elif line == 'Transitions:':
            header = 'Trans'
        elif line == 'Forcible events:':
            header = 'Force'

        elif header == 'Size':
            n_state_size = int(line.strip())
        elif header == 'Marker':
            marker_lines.append(line)    # either a number or *
        elif header == 'Vocal':
            vocal = line.split()        # state number, event number
            vocal_states[int(vocal[0])] = int(vocal[1])
        elif header == 'Force':
            pass
        elif header == 'Trans':
            trans.append([int(txt) for txt in line.split()])
        elif name is None:
            if line[-4:].lower() == '.ads':
                name = line[:-4]
            else:
                name = line
        else:
            raise exceptions.ModelError('Line %d has unknown format.' % linenum)

    if '*' in marker_lines:
        marker_lines = ['*']
    else:
        marker_lines = [ int(m) for m in marker_lines ]

    return name, n_state_size, marker_lines, vocal_states, trans


def convert_ads_file(ads_fname, coll):
    """
    Load ADS file, convert it to internal data format, and return the result.

    @param ads_fname: Filename of the ADS file to load.
    @type  ads_fname: C{str}

    @param coll: Collection to store the events of the automaton.
    @type  coll: L{Collection}

    @return: Converted automaton.
    @rtype: L{Automaton}
    """
    handle = open(ads_fname, 'r')
    _name, state_size, marker_lines, vocal_states, trans = read_ads_file(handle)

    assert len(vocal_states) == 0 # Vocal states are not supported atm.

    # Construct/query events of the automaton.
    evts = {}
    observable = True
    for src, evtnum, dest in trans:
        if evtnum not in evts:
            evt = coll.make_event(str(evtnum), evtnum & 1, observable, False)
            evts[evtnum] = evt

    aut = data_structure.Automaton(set(evts.itervalues()), coll)

    if marker_lines == ['*']:
        marker_states = None    # All states are marker state.
    else:
        marker_states = set(marker_lines)

    # Construct all states in the automaton.
    for num in range(state_size):
        aut.add_new_state(marker_states is None or num in marker_states, num)

    aut.set_initial(aut.get_state(0))

    for src, evtnum, dest in trans:
        srcstate = aut.get_state(src)
        deststate = aut.get_state(dest)
        aut.add_edge_data(srcstate, deststate, evts[evtnum])

    return aut
