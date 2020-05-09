#!/usr/bin/env python
# $Id: make_feasible_supervisor.py 538 2009-11-09 14:51:19Z hat $
"""
Convert a supervisor to one that makes transitions between two different
states only through observable events.
"""
import sys
# Make sure the installed version is used (is in the Python path).
site_packages = "%SITEPACKAGES%"
if not site_packages.startswith("%SITE") and site_packages not in sys.path:
    # Installed version, prefix installed path.
    sys.path = [site_packages] + sys.path


from automata import frontend

class MakeFeasibleSupervisorApplication(frontend.Application):
    def __init__(self):
        cmd = 'make_feasible_supervisor'
        desc = 'Convert a supervisor to one that makes transitions between ' \
               'two different states only through observable events.'
        frontend.Application.__init__(self, cmd, desc)

    def add_options(self):
        self.add_parm(frontend.CmdParm('plant', frontend.EXIST_AUT,
                                       'p', 'plant model'))

        self.add_parm(frontend.CmdParm('supervisor', frontend.EXIST_AUT,
                                       's', 'supervisor model'))

        self.add_parm(frontend.CmdParm('feas_sup', frontend.AUT,
                                       'o>', 'feasible supervisor filename'))

    def main(self, args):
        frontend.make_feasible_supervisor(args['plant'], args['supervisor'],
                                          args['feas_sup'])

if __name__ == '__main__':
    app = MakeFeasibleSupervisorApplication()
    app.run()

