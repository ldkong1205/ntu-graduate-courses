#!/usr/bin/env python
# $Id: make_abstraction.py 538 2009-11-09 14:51:19Z hat $
"""
Create an automaton abstraction of an input file.
"""
import sys
# Make sure the installed version is used (is in the Python path).
site_packages = "%SITEPACKAGES%"
if not site_packages.startswith("%SITE") and site_packages not in sys.path:
    # Installed version, prefix installed path.
    sys.path = [site_packages] + sys.path


from automata import frontend

class MakeAbstractionApplication(frontend.Application):
    def __init__(self):
        cmd = 'make_abstraction'
        desc = 'Create an automaton abstraction of an input file.'
        frontend.Application.__init__(self, cmd, desc)

    def add_options(self):
        self.add_parm(frontend.CmdParm('input_name', frontend.EXIST_AUT,
                                       '<', 'source automaton'))

        self.add_parm(frontend.CmdParm('tgtevt_names', frontend.EVTLIST,
                                       'e+', 'list of preserved events'))

        self.add_parm(frontend.CmdParm('output_name', frontend.AUT,
                                       'o>', 'name of the abstraction'))


    def main(self, args):
        frontend.make_abstraction(args['input_name'], args['tgtevt_names'],
                                  args['output_name'])


if __name__ == '__main__':
    app = MakeAbstractionApplication()
    app.run()

