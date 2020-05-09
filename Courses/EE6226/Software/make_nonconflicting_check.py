#!/usr/bin/env python
# $Id: make_nonconflicting_check.py 752 2010-06-23 12:43:03Z hat $
"""
Check whether a set of automata are nonconflicting with each other.
"""
import sys
# Make sure the installed version is used (is in the Python path).
site_packages = "%SITEPACKAGES%"
if not site_packages.startswith("%SITE") and site_packages not in sys.path:
    # Installed version, prefix installed path.
    sys.path = [site_packages] + sys.path


from automata import frontend

class MakeNonConflictingCheckApplication(frontend.Application):
    def __init__(self):
        cmd = 'make_nonconflicting_check'
        desc = 'Check whether a set of automata are nonconflicting with ' \
               'each other.'
        frontend.Application.__init__(self, cmd, desc)

    def add_options(self):
        self.add_parm(frontend.CmdParm('aut_names', frontend.AUTLIST,
                                       'i+<', 'list of your input automata'))

        self.add_parm(frontend.CmdParm('use_heuristic', frontend.BOOL,
                                        'r', 'use hueristic order'))

    def main(self, args):
        frontend.make_nonconflicting_check(args['aut_names'],
                                           args['use_heuristic'])

if __name__ == '__main__':
    app = MakeNonConflictingCheckApplication()
    app.run()

