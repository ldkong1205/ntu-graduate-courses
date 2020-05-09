from automata import frontend, weighted_frontend, row_vector,tools

#reqs = tools.convert("new-example-requirement")
#plant = tools.convert("new-example-a new-example-b new-example-c new-example-d new-example-e new-example-f")

#operator = 0
#rvecs = 0
L = 300
#weighted_frontend.make_greedy_time_optimal_supervisor(plant, reqs, "{(a,c),(a,e),(c,e),(b,d),(b,f),(d,f)}","new-example-sup-0.cfg",L)
#tools.filter_results("new-example-sup-0.cfg", "new-example-sup-0-unweighted.cfg" )


reqs = tools.convert("Z1SPEC Z2SPEC Z3SPEC Z4SPEC WS1SPEC WS2SPEC WS3SPEC IPSSPEC COUNTJOBSSPEC-3jobs MOVEALLSPEC")
plant = tools.convert("AGV1 AGV2 AGV3 AGV4 AGV5")

weighted_frontend.make_greedy_time_optimal_supervisor(plant, reqs, "{(11,20),(11,23),(13,20),(13,23),(18,33),(18,31),(24,33),(24,31),(21,41),(21,44),(26,41),(26,44),(40,51),(40,53),(43,51),(43,53),(32,50),(46,50),(32,46),(12,34),(28,42),(10,22),(11,22),(13,22),(11,24),(13,24),(10,20),(10,23),(12,20),(12,23),(20,31),(20,33),(26,31),(26,33),(18,32),(18,34),(24,32),(24,34),(18,41),(18,44),(28,41),(28,44),(21,40),(21,46),(26,40),(26,46),(40,50),(40,52),(43,50),(43,52),(42,51),(42,53),(44,51),(44,53)}","AGV-example-sup.cfg", L)
tools.filter_results("AGV-example-sup.cfg", "AGV-example-sup.cfg-unweighted.cfg" )


#operator = 1
#rvecs = row_vector.row_vector_compute(plant,reqs, "{(a,c),(a,e),(c,e),(b,d),(b,f),(d,f)}", "vectors.cfg", operator)
#weighted_frontend.make_greedy_time_optimal_supervisor_row_vectors(plant, reqs, "{(a,c),(a,e),(c,e),(b,d),(b,f),(d,f)}","new-example-sup-1.cfg", rvecs, operator)
#tools.filter_results("new-example-sup-1.cfg", "new-example-sup-1-unweighted.cfg" )
#operator = 2
#rvecs = row_vector.row_vector_compute(plant,reqs, "{(a,c),(a,e),(c,e),(b,d),(b,f),(d,f)}", "vectors.cfg", operator)
#weighted_frontend.make_greedy_time_optimal_supervisor_row_vectors(plant, reqs, "{(a,c),(a,e),(c,e),(b,d),(b,f),(d,f)}","new-example-sup-2.cfg", rvecs, operator)
#tools.filter_results("new-example-sup-2.cfg", "new-example-sup-2-unweighted.cfg" )

