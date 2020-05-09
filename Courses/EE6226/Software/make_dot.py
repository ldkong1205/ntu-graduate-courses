#!/usr/bin/env python
# $Id: make_dot.py 538 2009-11-09 14:51:19Z hat $
"""
Convert an automaton to the Graphviz DOT format.
After the conversion, use Graphviz to display the automaton.
"""
import sys
# Make sure the installed version is used (is in the Python path).
site_packages = "%SITEPACKAGES%"
if not site_packages.startswith("%SITE") and site_packages not in sys.path:
    # Installed version, prefix installed path.
    sys.path = [site_packages] + sys.path


from automata import frontend

class MakeDotApplication(frontend.Application):
    def __init__(self):
        cmd = 'make_dot'
        desc = 'Convert an automaton to the Graphviz DOT format.'
        frontend.Application.__init__(self, cmd, desc)

    def add_options(self):
        self.add_parm(frontend.CmdParm('aut_name', frontend.EXIST_AUT,
                                       'i<', 'model'))

        self.add_parm(frontend.CmdParm('dot_name', frontend.DOT,
                                       'o>', 'target Graphviz name'))

    def main(self, args):
        frontend.make_dot(args['aut_name'], args['dot_name'])

if __name__ == '__main__':
    app = MakeDotApplication()
    app.run()

