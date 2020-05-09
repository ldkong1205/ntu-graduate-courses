#!/usr/bin/env python
# $Id: make_supervisor.py 672 2010-03-24 10:26:31Z hat $
"""
Compute the supremal controllable and normal sublanguage of a plant with
respect to a specification. The alphabet of the specification need not be
the same as that of the plant.
"""
import sys
# Make sure the installed version is used (is in the Python path).
site_packages = "%SITEPACKAGES%"
if not site_packages.startswith("%SITE") and site_packages not in sys.path:
    # Installed version, prefix installed path.
    sys.path = [site_packages] + sys.path


from automata import frontend

class MakeSupervisorApplication(frontend.Application):
    def __init__(self):
        cmd = 'make_supervisor'
        desc = 'Compute the supremal controllable and normal sublanguage of ' \
               'a plant with respect to a requirement model.'
        frontend.Application.__init__(self, cmd, desc)

    def add_options(self):
        self.add_parm(frontend.CmdParm('plants', frontend.AUTLIST,
                                       '+p', 'plant models'))
        self.add_parm(frontend.CmdParm('specs', frontend.AUTLIST,
                                       '+r', 'requirement models'))
        self.add_parm(frontend.CmdParm('supervisor', frontend.AUT,
                                       'so>', 'supervisor'))

    def main(self, args):
        frontend.make_supervisor(args['plants'], args['specs'],
                                 args['supervisor'])

if __name__ == '__main__':
    app = MakeSupervisorApplication()
    app.run()

