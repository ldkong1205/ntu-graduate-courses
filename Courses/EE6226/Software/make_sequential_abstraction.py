#!/usr/bin/env python
# $Id: make_sequential_abstraction.py 538 2009-11-09 14:51:19Z hat $
"""
Compute an automaton abstraction of product of a number of automata
Each automaton must be standardized, i.e. the event tau must be contained.
"""
import sys
# Make sure the installed version is used (is in the Python path).
site_packages = "%SITEPACKAGES%"
if not site_packages.startswith("%SITE") and site_packages not in sys.path:
    # Installed version, prefix installed path.
    sys.path = [site_packages] + sys.path


from automata import frontend

class MakeSequentialAbstractionApplication(frontend.Application):
    def __init__(self):
        cmd = 'make_sequential_abstraction'
        desc = 'Compute an automaton abstraction of product of a number of ' \
               'automata.'
        frontend.Application.__init__(self, cmd, desc)

    def add_options(self):
        self.add_parm(frontend.CmdParm('aut_names', frontend.AUTLIST,
                                       'i+', 'list of your input automata'))
        self.add_parm(frontend.CmdParm('psvevt_names', frontend.EVTLIST,
                                       'e+', 'list of preserved events'))
        self.add_parm(frontend.CmdParm('output', frontend.AUT,
                                       'o>', 'abstraction'))

    def main(self, args):
        frontend.make_sequential_abstraction(args['aut_names'],
                                             args['psvevt_names'],
                                             args['output'])

if __name__ == '__main__':
    app = MakeSequentialAbstractionApplication()
    app.run()

