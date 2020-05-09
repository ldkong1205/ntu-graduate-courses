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
        newline = string.replace(line, "[weighted-automaton]", "[automation]" )
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


plant = convert("wmw-M1 wmw-M2")
reqs = convert("WMW-SPEC3 WMW-SPEC4 WMW-SPEC51 WMW-SPEC52")

weighted_frontend.make_greedy_time_optimal_supervisor(plant, reqs, "{(b11,a21),(b22,a12)}","WMW-example-sup.cfg")
filter_results("WMW-example-sup.cfg")
frontend.make_abstraction("WMW-example-sup_unweight.cfg", "a11, a12, a21, a22, b11, b12, b21, b22", "WMW-example-simsup.cfg")
frontend.make_dot("WMW-example-simsup.cfg", "WMW-example-simsup.dot")

#plant = convert("type2_r1br2/r1 type2_r1br2/r2")
#reqs = convert("type2_r1br2/b1")
#super_name = convert("type2_r1br2/Greedy-sup")

#weighted_frontend.make_greedy_time_optimal_supervisor(plant, reqs, "type2",super_name)



