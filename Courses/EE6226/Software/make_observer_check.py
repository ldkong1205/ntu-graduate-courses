#!/usr/bin/env python
# $Id: make_observer_check.py 729 2010-04-16 11:00:51Z hat $
"""
Verify whether the observer property holds, and if not, list the events that
break it.
"""
import sys
# Make sure the installed version is used (is in the Python path).
site_packages = "%SITEPACKAGES%"
if not site_packages.startswith("%SITE") and site_packages not in sys.path:
    # Installed version, prefix installed path.
    sys.path = [site_packages] + sys.path


from automata import frontend

class MakeObserverCheckApplication(frontend.Application):
    def __init__(self):
        cmd = 'make_observer_check'
        desc = 'Verify whether the observer property holds, and if not, ' \
               'list the events that break it.'
        frontend.Application.__init__(self, cmd, desc)

    def add_options(self):
        self.add_parm(frontend.CmdParm('input_name', frontend.EXIST_AUT,
                                       '<', 'source automaton'))

        self.add_parm(frontend.CmdParm('obs_names', frontend.EVTLIST,
                                       'e+', 'list of observable events'))

    def main(self, args):
        frontend.make_observer_check(args['input_name'], args['obs_names'])


if __name__ == '__main__':
    app = MakeObserverCheckApplication()
    app.run()

