#
# $Id: weighted_product.py 634 2010-01-28 11:46:01Z hat $
#
"""
Weighted product calculation.
"""
from automata import common, algorithm, product

def n_ary_weighted_product(auts, add_fn, delete_aut = False,
                            report_progress = False):
    """
    N-ary weighted automata product.

    @param auts: Input automata.
    @type  auts: C{list} of L{WeightedAutomaton}

    @param add_fn: Name of the function to use for calculating the weight
                   at new edge.
    @type  add_fn: L{algorithm.SUM_EDGE_WEIGHTS},
                   L{algorithm.EQUAL_WEIGHT_EDGES},
                   L{algorithm.FIRST_EDGE}, or L{algorithm.FIRST_EDGE}

    @param delete_aut: Routine is allowed to delete the provided automata.
    @type  delete_aut: C{bool}

    @param report_progress: Output progress of the computation.
    @type  report_progress: C{bool}

    @return: Resulting weighted automaton.
    @rtype:  L{WeightedAutomaton}
    """
    if report_progress:
        common.print_line("Must do %d weighted product computations." \
                                                            % (len(auts) - 1))

    props = algorithm.ManagerProperties(auts[0].collection)
    props.aut_type = algorithm.WEIGHTED_AUT
    props.marker_func = algorithm.MARKED_ALL
    props.explore_mgr = algorithm.ORIGINAL_STATE
    props.edge_calc = add_fn

    prod, prod_map =  product.do_n_ary_product_map(props, auts, False)
    prod_map.clear()

    if delete_aut:
        for aut in auts:
            aut.clear()

    return prod

