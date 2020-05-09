#!/usr/bin/env python
# $Id: make_get_size.py 538 2009-11-09 14:51:19Z hat $
"""
Output number of states and transitions of an automaton.
"""
import sys
# Make sure the installed version is used (is in the Python path).
site_packages = "%SITEPACKAGES%"
if not site_packages.startswith("%SITE") and site_packages not in sys.path:
    # Installed version, prefix installed path.
    sys.path = [site_packages] + sys.path


from automata import frontend

class MakeGetSizeApplication(frontend.Application):
    def __init__(self):
        cmd = 'make_get_size'
        desc = 'Output number of states and transitions of an automaton.'
        frontend.Application.__init__(self, cmd, desc)

    def add_options(self):
        self.add_parm(frontend.CmdParm('aut_name', frontend.EXIST_AUT,
                                       'i<', 'model'))

    def main(self, args):
        frontend.make_get_size(args['aut_name'])

if __name__ == '__main__':
    app = MakeGetSizeApplication()
    app.run()

