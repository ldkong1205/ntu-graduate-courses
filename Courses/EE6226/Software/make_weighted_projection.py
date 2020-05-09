#!/usr/bin/env python
# $Id: make_weighted_projection.py 538 2009-11-09 14:51:19Z hat $
"""
Perform weighted projection.
"""
import sys
# Make sure the installed version is used (is in the Python path).
site_packages = "%SITEPACKAGES%"
if not site_packages.startswith("%SITE") and site_packages not in sys.path:
    # Installed version, prefix installed path.
    sys.path = [site_packages] + sys.path


from automata import frontend, weighted_frontend

class MakeWeightedProjectionApplication(frontend.Application):
    def __init__(self):
        cmd = 'make_weighted_projection'
        desc = 'Perform weighted projection.'
        frontend.Application.__init__(self, cmd, desc)

    def add_options(self):
        self.add_parm(frontend.CmdParm('input', frontend.EXIST_AUT,
                                       'i<', 'source automaton'))
        self.add_parm(frontend.CmdParm('psvevt_names', frontend.EVTLIST,
                                       'e+', 'list of preserved events'))
        self.add_parm(frontend.CmdParm('output', frontend.AUT,
                                       'o>', 'name of the abstraction'))

    def main(self, args):
        weighted_frontend.make_weighted_projection(args['input'],
                                                   args['psvevt_names'],
                                                   args['output'])

if __name__ == '__main__':
    app = MakeWeightedProjectionApplication()
    app.run()

