from automata import frontend, weighted_frontend, row_vector,tools

reqs  = tools.convert("new-example-requirement")
plant = tools.convert("new-example-a new-example-b new-example-c new-example-d new-example-e new-example-f")

operator = 0
rvecs = 0
L = 2

weighted_frontend.make_greedy_time_optimal_supervisor(plant, reqs, "{(a,c),(a,e),(c,e),(b,d),(b,f),(d,f)}","new-example-sup-0.cfg",L)
tools.filter_results("new-example-sup-0.cfg", "new-example-sup-0-unweighted.cfg" )
weighted_frontend.LBE_make_greedy_time_optimal_supervisor(plant, reqs, "{(a,c),(a,e),(c,e),(b,d),(b,f),(d,f)}")

#operator = 1
#rvecs = row_vector.row_vector_compute(plant,reqs, "{(a,c),(a,e),(c,e),(b,d),(b,f),(d,f)}", "vectors.cfg", operator)
#weighted_frontend.make_greedy_time_optimal_supervisor_row_vectors(plant, reqs, "{(a,c),(a,e),(c,e),(b,d),(b,f),(d,f)}","new-example-sup-1.cfg", rvecs, operator)
#tools.filter_results("new-example-sup-1.cfg", "new-example-sup-1-unweighted.cfg" )
#operator = 2
#rvecs = row_vector.row_vector_compute(plant,reqs, "{(a,c),(a,e),(c,e),(b,d),(b,f),(d,f)}", "vectors.cfg", operator)
#weighted_frontend.make_greedy_time_optimal_supervisor_row_vectors(plant, reqs, "{(a,c),(a,e),(c,e),(b,d),(b,f),(d,f)}","new-example-sup-2.cfg", rvecs, operator)
#tools.filter_results("new-example-sup-2.cfg", "new-example-sup-2-unweighted.cfg" )

print "******Generation of F"
weighted_frontend.FK_row_vector(plant, reqs, "{(a,c),(a,e),(c,e),(b,d),(b,f),(d,f)}")