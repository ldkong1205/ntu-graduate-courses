import automata
from automata import abstraction, algorithm, collection, common, \
                     compute_weight, conversion, frontend, product, \
                     supervisor, taskresource, weighted_projection, \
                     weighted_equality, weighted_product, maxplus, \
                     weighted_structure, weighted_supervisor, weighted_frontend

MARKER_STATE = 0   #: Marker state computation (weight = 0)
CONTROLLABLE = 1   #: State has only controllable edges (min of weights)
UNCONTROLLABLE = 2 #: State has uncontrollable edges (max of weights)

def convert(txt):
        names = txt.split()
        return ",".join(["%s.cfg" % name for name in names])

def scalar_compute(avec):
    assert avec.num_row == 1
    bvec = maxplus.make_matrix(0, avec.num_col, avec.num_row)
    cflag = 1
    for rnum in range(avec.num_row):
        for cvar in range(bvec.num_col):
            for evar in range(avec.num_col):
                rtmp = maxplus.oplus(avec.data[rnum][evar],bvec.data[evar][cvar])
                if cflag == 1:
                    rval = rtmp
                    cflag = 0
                else:
                  if rtmp is maxplus.INFINITE :
                     rval = rtmp;
                  elif rtmp is maxplus.EPSILON:
                     rval = rval
                  elif rval is maxplus.INFINITE:
                     rval = rval
                  elif rval is maxplus.EPSILON:
                     rval = rtmp
                  else:
                     if rtmp > rval :
                       rval = rtmp
    return rval

def scalar_compare(ascalar, bscalar):
    if ascalar is maxplus.INFINITE:
        if bscalar is maxplus.INFINITE:
           return 0
        else:
           return 1
    if ascalar is maxplus.EPSILON:
        if bscalar is maxplus.EPSILON:
            return 0
        else:
            return -1
    if bscalar is maxplus.INFINITE:
        return -1
    if bscalar is maxplus.EPSILON:
        return 1
    if ascalar == bscalar:
        return 0
    if ascalar > bscalar:
        return 1
    if ascalar < bscalar:
        return -1

def minimal_compute(avec, bvec):
    assert avec.num_row == 1
    assert bvec.num_row == 1
    rval = maxplus.make_matrix(0,1,avec.num_col)
    flag = -1
    for cvar in range(avec.num_col):
         r1 = avec.data[0][cvar]
         r2 = bvec.data[0][cvar]
         if scalar_compare(r1,r2) == -1:
            rval.data[0][cvar] = r1
            flag = 0
         elif scalar_compare(r1,r2) == 1:
            rval.data[0][cvar] = r2
            flag = 0
    return rval, flag

def minimal_compare(ascalar, bscalar):
    if ascalar is maxplus.INFINITE:
        if bscalar is maxplus.INFINITE:
           return 0
        else:
           return 1
    if ascalar is maxplus.EPSILON:
        if bscalar is maxplus.EPSILON:
            return 0
        else:
            return -1
    if bscalar is maxplus.INFINITE:
        return -1
    if bscalar is maxplus.EPSILON:
        return 1
    if ascalar == bscalar:
        return 0
    if ascalar > bscalar:
        return 1
    if ascalar < bscalar:
        return -1

def vector_equal_compare(a ,b):
   if a.num_row != b.num_row:
      return -1
   if a.num_col != b.num_col:
      return -1
   for cvar in range(a.num_col):
         r1 = a.data[0][cvar]
         r2 = b.data[0][cvar]
         if scalar_compare(r1, r2) != 0:
            return -1
   return 0

def compute_state_row_vector(aut, marker_valfn, nonmarker_valfn, eventdata, operate_class):
        """
        Compute row vector of each state

        Attach a weight to each state, and iteratively update these weights until a
        stable situation is found.
         - Initial setup:
            - Marker states have weight 'marker_valfn(state)'.
            - Other states have weight 'nonmarker_valfn(state)'
         - Update rules:

        Update until all weights are stable.

        @param aut: Weighted automaton.
        @type  aut: L{WeightedAutomaton}

        @return: Dictionary of states to their row vector.
        @rtype:  C{dict} of L{WeightedState} to (C{int} or C{None} if infinite)

        @todo: THIS CODE LOOKS LIKE A DUPLICATE
        """
        # 1. Compute state information for each state.
        computation = compute_weight.make_state_info_mapping(aut)

        # 2. Initialize weights.
        row_vectors = {} #: Map of states to a set of row vectors.
        need_to_update = set()
        for state, comp in computation.iteritems():
            if state.number  == MARKER_STATE:
                row_vectors[state] = marker_valfn(state)
            else:
                row_vectors[state] = nonmarker_valfn(state)
            need_to_update.update(compute_weight.pred_states(state))
        count = 0
        # 3. Iteratively update the row vector with new ones until stable.
        while True:
            count = count + 1
            # Compute new row_vectors
            new_need_to_update = set()
            for state, comp in computation.iteritems():
                   if state not in need_to_update:
                      continue

                   if comp[0] == MARKER_STATE:
                      continue

                   for evt, statedestlist in comp[1]:
                      dest = (statedestlist[0])[1]
                      tmp_vector = maxplus.otimes_mat_mat(row_vectors[state], eventdata[evt].matHat)

                      if vector_equal_compare(tmp_vector ,row_vectors[dest])!= 0:
                           new_need_to_update.update(compute_weight.pred_states(state))

                      if operate_class == 1 :
                         scalar1 = scalar_compute(tmp_vector)
                         scalar2 = scalar_compute(row_vectors[dest])
                         if scalar_compare( scalar1 , scalar2) == -1 :
                            row_vectors[dest] = tmp_vector
                      elif operate_class == 2:
                            row_vectors[dest],f = minimal_compute(tmp_vector,row_vectors[dest])

            if len(new_need_to_update) == 0:
                       break

            need_to_update = new_need_to_update

        for state, comp in computation.iteritems():
                 M = row_vectors[state]
        return row_vectors


def row_vector_compute(plant,req_names, evt_pairs, row_vector_names, operator_class):
         coll = collection.Collection()
         comp_list = weighted_frontend.load_weighted_automata(coll, plant, False, True)
         req_list  = frontend.load_automata(coll, req_names, False, True)
         evt_pairs = taskresource.process_event_pairs(coll, req_list, evt_pairs)
         result    = taskresource.compute_custom_eventdata(comp_list, evt_pairs)
         if result is None:
              common.print_line('Could not compute the event data from the '
                          'components and event pairs\n'
                          'Perhaps they are inconsistent?')
              return

         eventdata, heap_len = result

         plant = weighted_product.n_ary_weighted_product(comp_list,
                                                algorithm.EQUAL_WEIGHT_EDGES)
         requirement = product.n_ary_unweighted_product(req_list)

         for comp in comp_list:
               comp.clear()
         del comp_list

         wsup = compute_weight.compute_weighted_supremal(plant, requirement)
         if wsup is None:
                 return None
         requirement.clear()
         del requirement

         row_zero_mat = maxplus.make_rowmat(0, heap_len)
         row_epsilon_mat = maxplus.make_rowmat(maxplus.INFINITE, heap_len)

         marker_valfn = lambda state: row_zero_mat
         nonmarker_valfn = lambda state: row_epsilon_mat

         row_vecs = compute_state_row_vector(wsup, marker_valfn, nonmarker_valfn, eventdata, operator_class)

         return row_vecs

def enhanced_row_vector_compute(plant,req_names, evt_pairs, row_vector_names, operator_class):
         coll = collection.Collection()
         comp_list = weighted_frontend.load_weighted_automata(coll, plant, False, True)
         req_list  = frontend.load_automata(coll, req_names, False, True)
         evt_pairs = taskresource.process_event_pairs(coll, req_list, evt_pairs)
         result    = taskresource.compute_custom_eventdata(comp_list, evt_pairs)
         if result is None:
              common.print_line('Could not compute the event data from the '
                          'components and event pairs\n'
                          'Perhaps they are inconsistent?')
              return

         eventdata, heap_len = result

         plant       = do_n_ary_product_map(comp_list)
         for comp in comp_list:
               comp.clear()
         del comp_list

         wsup = plant.get_automaton()
         if wsup is None:
                 return None

         row_zero_mat = maxplus.make_rowmat(0, 1)
         row_epsilon_mat = maxplus.make_rowmat(maxplus.INFINITE, 1)

         marker_valfn = lambda state: row_zero_mat
         nonmarker_valfn = lambda state: row_epsilon_mat

         row_vecs = enhance_compute_state_row_vector(wsup, marker_valfn, nonmarker_valfn, eventdata, operator_class)

         return row_vecs

def do_n_ary_product_map(auts):

    props             = algorithm.ManagerProperties(auts[0].collection)
    props.aut_type    = algorithm.WEIGHTED_AUT
    props.marker_func = algorithm.MARKED_ALL
    props.explore_mgr = algorithm.ORIGINAL_STATE
    props.edge_calc   = algorithm.EQUAL_WEIGHT_EDGES

    has_plant, has_req, has_other = False, False, False
    result_alphabet = set()
    for aut in auts:
        # Verify that all automata use the same collection, and have an initial
        # state.
        assert aut.collection is auts[0].collection
        assert aut.initial is not None

        result_alphabet.update(aut.alphabet)

        if aut.aut_kind == 'plant':
            has_plant = True
        elif aut.aut_kind == 'requirement':
            has_req = True
        else:
            has_other = True

    props.alphabet = result_alphabet

    if has_plant and not has_req and not has_other:
        result_kind = 'plant'
    elif not has_plant and has_req and not has_other:
        result_kind = 'requirement'
    else:
        result_kind = 'unknown'

    # Construct a mapping from event to a boolean whether or not each automaton
    # participates with the event.
    participate = {}
    for evt in result_alphabet:
        participate[evt] = [evt in aut.alphabet for aut in auts]

    mgr = algorithm.Manager(props)
    mgr.set_initial(tuple(aut.initial for aut in auts))
    while True:
        orig_state = mgr.get_next()
        if orig_state is None:
            break

        # Find current edges, collect disabled events from the orig_state.
        edges = [] #: List of lists with edges of each automaton.
        disabled = set() #: Disabled events
        for aut, state in zip(auts, orig_state):
            aut_edges = []
            aut_events = set()
            for edge in state.get_outgoing():
                aut_edges.append(edge)
                aut_events.add(edge.label)

            edges.append(aut_edges)
            disabled.update(aut.alphabet.difference(aut_events))

        # Do every event that is enabled.
        for evt in result_alphabet.difference(disabled):
            product.add_new_states(orig_state, evt, participate[evt], edges, mgr,
                           [], [])

    prod_aut = mgr
    prod_aut.aut_kind = result_kind
   # mapping = mgr.get_mapping()

    return prod_aut


def enhance_compute_state_row_vector(aut, marker_valfn, nonmarker_valfn, eventdata, operate_class):
        """
        Compute row vector of each state

        Attach a weight to each state, and iteratively update these weights until a
        stable situation is found.
         - Initial setup:
            - Marker states have weight 'marker_valfn(state)'.
            - Other states have weight 'nonmarker_valfn(state)'
         - Update rules:

        Update until all weights are stable.

        @param aut: Weighted automaton.
        @type  aut: L{WeightedAutomaton}

        @return: Dictionary of states to their row vector.
        @rtype:  C{dict} of L{WeightedState} to (C{int} or C{None} if infinite)

        @todo: THIS CODE LOOKS LIKE A DUPLICATE
        """
        # 1. Compute state information for each state.
        computation = {}

        for state in aut.get_states():
            if state.marked:
                computation[state] = (MARKER_STATE,)
              #  continue

            # Non-marked states
            edges = []  #: Edges collected so far
            controllable = True #: Collect controllable edges

            # Collect successor states from 'state' by event.
            evt_dests = {} #: event to list (weight, dest-state).
            controllable = True #: State has only edges with controllable events.
            for edge in state.get_outgoing():
                weight_dests = evt_dests.get(edge.label)
                if weight_dests is None:
                    weight_dests = []
                    evt_dests[edge.label] = weight_dests

                    controllable = (controllable and edge.label.controllable)

                weight_dests.append((edge.weight, edge.succ))

            if controllable:
                # Keep all edges (all have controllable event label).
                edges = list(evt_dests.iteritems())
                # assert len(edges) > 0 # Otherwise cannot compute min or max.
                computation[state] = (CONTROLLABLE, edges)
            else:
                # Only keep edges with uncontrollable event labels.
                edges = [(evt, dests) for evt, dests in evt_dests.iteritems()
                                           if not evt.controllable]
                #assert len(edges) > 0 # Otherwise cannot compute min or max.
                computation[state] = (UNCONTROLLABLE, edges)

        # 2. Initialize weights.
        row_vectors = {} #: Map of states to a set of row vectors.
        need_to_update = set()
        for state in computation.iteritems():
           if state[0].number  == MARKER_STATE:
               row_vectors[state[0]] = marker_valfn(state[0])
           else:
               row_vectors[state[0]] = nonmarker_valfn(state[0])
           need_to_update.update(compute_weight.pred_states(state[0]))

        count = 0
        # 3. Iteratively update the row vector with new ones until stable.
        while True:
            count = count + 1
            # Compute new row_vectors
            update_f = 0
            for state, comp in computation.iteritems():
                   if state not in need_to_update:
                      continue

                   if comp[0] == MARKER_STATE:
                      continue

                   for evt, statedestlist in comp[1]:
                      dest = (statedestlist[0])[1]
                      tmp_vector = maxplus.otimes_mat_mat(row_vectors[state], eventdata[evt].matHat)

                      if operate_class == 1 :
                         scalar1 = scalar_compute(tmp_vector)
                         scalar2 = scalar_compute(row_vectors[dest])
                         if scalar_compare( scalar1 , scalar2) == -1 :
                            row_vectors[dest] = tmp_vector
                            update_f = 1
                      elif operate_class == 2:
                            flag = -1
                            row_vectors[dest], flag = minimal_compute(tmp_vector,row_vectors[dest])
                            if flag == 0:
                                update_f = 1

            if update_f == 0:
                       break

        return row_vectors
