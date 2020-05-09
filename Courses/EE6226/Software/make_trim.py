#!/usr/bin/env python
# $Id: make_trim.py 730 2010-04-16 12:01:22Z hat $
"""
Trim automaton (reduce to reachable and coreachable states).
"""
import sys
# Make sure the installed version is used (is in the Python path).
site_packages = "%SITEPACKAGES%"
if not site_packages.startswith("%SITE") and site_packages not in sys.path:
    # Installed version, prefix installed path.
    sys.path = [site_packages] + sys.path


from automata import frontend

class MakeTrimApplication(frontend.Application):
    def __init__(self):
        cmd = 'make_trim'
        desc = 'Trim automaton (reduce to reachable and coreachable states).'
        frontend.Application.__init__(self, cmd, desc)

    def add_options(self):
        self.add_parm(frontend.CmdParm('input_name', frontend.EXIST_AUT,
                                       '<', 'source automaton'))

        self.add_parm(frontend.CmdParm('output_name', frontend.AUT,
                                       'o>', 'name of the result'))


    def main(self, args):
        frontend.make_trim(args['input_name'], args['output_name'])


if __name__ == '__main__':
    app = MakeTrimApplication()
    app.run()

