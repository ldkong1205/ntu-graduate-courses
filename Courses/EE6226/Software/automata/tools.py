from automata import frontend, weighted_frontend, row_vector

def convert(txt):
    names = txt.split()
    return ",".join(["%s.cfg" % name for name in names])

def filter_results(super_name, new_super_name):
    # replace the [weighted-automaton] with [automation]
    # remove weights in transitions

    import fileinput
    import string

    fout = open(new_super_name, "w")

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




