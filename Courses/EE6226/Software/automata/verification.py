#
# $Id: verification.py 591 2010-01-18 08:41:51Z hat $
#
from automata import supervisor, product

def language_inclusion(aut1, aut2):
    """
    Verify that language of L{aut1} is a sub-set of the language of L{aut2}.

    @param aut1: Automaton with smallest language.
    @type  aut1: L{Automaton}

    @param aut2: Automaton with biggest language.
    @type  aut2: L{Automaton}

    @return: Indication whether the condition holds (L{aut1} has a language
             subset of L{aut2}).
    @rtype:  C{bool}
    """
    aut1 = supervisor.unweighted_determinization(aut1)

    aut2 = supervisor.unweighted_determinization(aut2)
    aut2 = supervisor.complement(aut2)

    prod = product.n_ary_unweighted_product([aut1, aut2])
    for state in prod.get_states():
        if state.marked:
            return False

    return True

def language_equivalence(aut1, aut2):
    return language_inclusion(aut1, aut2) and language_inclusion(aut2, aut1)

