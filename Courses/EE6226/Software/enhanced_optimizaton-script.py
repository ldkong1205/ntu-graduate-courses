from automata import frontend, weighted_frontend, row_vector,tools

#plant = convert("algorithm2-M algorithm2-M")
#reqs  = convert("algorithm2-SPEC1 algorithm2-SPEC1")
#row_vector_compute(plant, reqs, "{(a,c),(b,c),(a,d),(c,d)}", 1)

plant = tools.convert("wmw-M1 wmw-M2")
reqs  = tools.convert("WMW-SPEC3 WMW-SPEC4 WMW-SPEC51 WMW-SPEC52")
operator = 1
# for algorithm 2, the operator is one; for algorithm 3, the operator is two
rvecs = row_vector.row_vector_compute(plant,reqs, "{(b11,a21),(b22,a12)}", "vectors.cfg", operator)

weighted_frontend.make_greedy_time_optimal_supervisor(plant, reqs, "{(b11,a21),(b22,a12)}","WMW-example-sup.cfg", rvecs)
tools.filter_results("WMW-example-sup.cfg", "WMW-unweight.cfg")
frontend.make_abstraction("WMW-unweight.cfg", "a11, a12, a21, a22, b11, b12, b21, b22", "WMW-example-simsup.cfg")
frontend.make_dot("WMW-example-simsup.cfg", "WMW-example-simsup.dot")
