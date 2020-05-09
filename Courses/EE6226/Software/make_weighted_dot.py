#!/usr/bin/env python
# $Id: make_weighted_dot.py 538 2009-11-09 14:51:19Z hat $
"""
Convert weighted automaton to Graphviz DOT format.
"""
import sys
# Make sure the installed version is used (is in the Python path).
site_packages = "%SITEPACKAGES%"
if not site_packages.startswith("%SITE") and site_packages not in sys.path:
    # Installed version, prefix installed path.
    sys.path = [site_packages] + sys.path


from automata import frontend, weighted_frontend

class MakeWeightedDotApplication(frontend.Application):
    def __init__(self):
        cmd = 'make_weighted_dot'
        desc = 'Convert weighted automaton to Graphviz DOT format.'
        frontend.Application.__init__(self, cmd, desc)

    def add_options(self):
        self.add_parm(frontend.CmdParm('aut_name', frontend.EXIST_AUT,
                                       'i<', 'weighted model'))
        self.add_parm(frontend.CmdParm('dot_name', frontend.DOT,
                                       'o>', 'target Graphviz name'))

    def main(self, args):
        weighted_frontend.make_weighted_dot(args['aut_name'], args['dot_name'])

if __name__ == '__main__':
    app = MakeWeightedDotApplication()
    app.run()

