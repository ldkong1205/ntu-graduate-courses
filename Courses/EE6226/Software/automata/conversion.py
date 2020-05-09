#
# $Id: conversion.py 513 2009-10-21 07:35:11Z pthijs $
#
"""
Helper code to convert automata.
"""

from automata import data_structure, weighted_structure


def remove_weights(waut):
    """
    Remove the weights of weighted automaton L{waut}.

    @param waut: Weighted automaton.
    @type  waut: L{collection.WeightedAutomaton}

    @return: Equivalent unweighted automaton.
    @rtype:  L{collection.Automaton}
    """
    aut = data_structure.Automaton(waut.alphabet, waut.collection)
    aut.set_kind(waut.aut_kind)

    for wstat in waut.get_states():
        aut.add_new_state(wstat.marked, wstat.number)
    aut.set_initial(aut.get_state(waut.initial.number))

    for wstat in waut.get_states():
        src = aut.get_state(wstat.number)
        for wedge in wstat.get_outgoing():
            dest = aut.get_state(wedge.succ.number)
            aut.add_edge_data(src, dest, wedge.label)

    return aut

def add_weights(aut, edge_weight=0):
    """
    Add weights to unweighted automaton L{aut}.

    @param aut: Unweighted automaton.
    @type  aut: L{Automaton}

    @param edge_weight: Weight of each edge.
    @type  edge_weight: C{int}

    @return: Equivalent weighted automaton.
    @rtype:  L{WeightedAutomaton}
    """
    waut = weighted_structure.WeightedAutomaton(aut.alphabet, aut.collection)
    waut.set_kind(aut.aut_kind)

    for stat in aut.get_states():
        waut.add_new_state(stat.marked, stat.number)
    waut.set_initial(waut.get_state(aut.initial.number))

    for stat in aut.get_states():
        wsrc = waut.get_state(stat.number)
        for edge in stat.get_outgoing():
            wdest = waut.get_state(edge.succ.number)
            waut.add_edge_data(wsrc, wdest, edge.label, edge_weight)

    return waut
