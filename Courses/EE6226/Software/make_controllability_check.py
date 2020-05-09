#!/usr/bin/env python
# $Id: make_controllability_check.py 538 2009-11-09 14:51:19Z hat $
#
"""
Check whether a supervisor is controllable with respect to a plant.
"""
import sys
# Make sure the installed version is used (is in the Python path).
site_packages = "%SITEPACKAGES%"
if not site_packages.startswith("%SITE") and site_packages not in sys.path:
    # Installed version, prefix installed path.
    sys.path = [site_packages] + sys.path


from automata import frontend

class MakeControllabilityCheckApplication(frontend.Application):
    def __init__(self):
        cmd = 'make_controllability_check'
        desc = 'Check whether a supervisor is controllable with respect ' \
               'to a plant.'
        frontend.Application.__init__(self, cmd, desc)

    def add_options(self):
        self.add_parm(frontend.CmdParm('plant_name', frontend.EXIST_AUT,
                                       'p', 'plant model'))

        self.add_parm(frontend.CmdParm('sup_name', frontend.EXIST_AUT,
                                       's', 'supervisor model'))

    def main(self, args):
        frontend.make_controllability_check(args['plant_name'],
                                            args['sup_name'])

if __name__ == '__main__':
    app = MakeControllabilityCheckApplication()
    app.run()

