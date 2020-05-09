from automata import frontend, weighted_frontend

def convert(txt):
    names = txt.split()
    return ",".join(["%s.cfg" % name for name in names])

def filter_results(super_name):
    # replace the [weighted-automaton] with [automation]
    # remove weights in transitions

    import fileinput
    import string

    newname = string.replace(super_name,".cfg","_unweight.cfg")
    fout = open(newname, "w")

    transition_f = -1
    for line in fileinput.input(super_name):
        newline = string.replace(line, "[weighted-automaton]", "[automaton]" )
        s_index = string.find(newline,"transitions")
        linew = ""
        if transition_f is 0 or s_index is not -1:
           transition_f = 0;
           if s_index is -1:
              s_index = 0
           else:
              linew = "transitions = "

           var = 1
           while var == 1 :
                 phase_s = string.find(newline,"(", s_index)
                 if phase_s is -1:
                    break;
                 phase_e = string.find(newline,")", phase_s)
                 if phase_e is -1:
                    break;

                 phase = newline[phase_s+1:phase_e]
                 pindex1= string.find(phase,",")
                 pindex2= string.find(phase,",",pindex1+1)
                 pindex3= string.find(phase,",",pindex2+1)
                 newphase = phase[0:pindex3]

                 if newline[phase_e+1] is ",":
                    linew = linew + "("+ newphase +"),"
                 else:
                    linew = linew + "("+ newphase +")"
                 s_index = phase_e
        else:
                 linew = newline
        fout.writelines(linew)

    lines = fileinput.filelineno()
    fout.close()
    return;


reqs = convert("Z1SPEC Z2SPEC Z3SPEC Z4SPEC WS1SPEC WS2SPEC WS3SPEC IPSSPEC COUNTJOBSSPEC-5jobs MOVEALLSPEC")
plant = convert("AGV1 AGV2 AGV3 AGV4 AGV5")

weighted_frontend.make_greedy_time_optimal_supervisor(plant, reqs, "{(11,20),(11,23),(13,20),(13,23),(18,33),(18,31),(24,33),(24,31),(21,41),(21,44),(26,41),(26,44),(40,51),(40,53),(43,51),(43,53),(32,50),(46,50),(32,46),(12,34),(28,42),(10,22),(11,22),(13,22),(11,24),(13,24),(10,20),(10,23),(12,20),(12,23),(20,31),(20,33),(26,31),(26,33),(18,32),(18,34),(24,32),(24,34),(18,41),(18,44),(28,41),(28,44),(21,40),(21,46),(26,40),(26,46),(40,50),(40,52),(43,50),(43,52),(42,51),(42,53),(44,51),(44,53)}","AGV-example-sup.cfg")
filter_results("AGV-example-sup.cfg")
frontend.make_abstraction("AGV-example-sup_unweight.cfg", "11,10,13,12,21,18,20,22,23,24,26,28,33,34,31,32,41,40,42,43,44,46,51,50,53,52", "AGV-example-simsup.cfg")
frontend.make_dot("AGV-example-simsup.cfg", "AGV-example-simsup.dot")
weighted_frontend.compute_shortest_path(plant, reqs,  "{(11,20),(11,23),(13,20),(13,23),(18,33),(18,31),(24,33),(24,31),(21,41),(21,44),(26,41),(26,44),(40,51),(40,53),(43,51),(43,53),(32,50),(46,50),(32,46),(12,34),(28,42),(10,22),(11,22),(13,22),(11,24),(13,24),(10,20),(10,23),(12,20),(12,23),(20,31),(20,33),(26,31),(26,33),(18,32),(18,34),(24,32),(24,34),(18,41),(18,44),(28,41),(28,44),(21,40),(21,46),(26,40),(26,46),(40,50),(40,52),(43,50),(43,52),(42,51),(42,53),(44,51),(44,53)}")

#plant = convert("type2_r1br2/r1 type2_r1br2/r2")
#reqs = convert("type2_r1br2/b1")
#super_name = convert("type2_r1br2/Greedy-sup")

#weighted_frontend.make_greedy_time_optimal_supervisor(plant, reqs, "type2",super_name)



raw_input() 