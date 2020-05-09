#!/usr/bin/env python
# $Id: make_compute_shortest_path.py 717 2010-04-06 13:57:19Z hat $
"""
Compute shortest path with A* algorithm.

@note: The weight is associated with the event rather than the edge!
"""
import sys
# Make sure the installed version is used (is in the Python path).
site_packages = "%SITEPACKAGES%"
if not site_packages.startswith("%SITE") and site_packages not in sys.path:
    # Installed version, prefix installed path.
    sys.path = [site_packages] + sys.path


from automata import frontend, weighted_frontend

class ComputeShortestPathApplication(frontend.Application):
    def __init__(self):
        cmd = 'make_compute_shortest_path_type1'
        desc = 'Compute shortest path with A* algorithm'
        frontend.Application.__init__(self, cmd, desc)

    def add_options(self):
        self.add_parm(frontend.CmdParm('comp_names', frontend.AUTLIST, 'p',
                                'list of components (weighted automata)'))
        self.add_parm(frontend.CmdParm('req_names', frontend.AUTLIST, 'r',
                                'list of requirements (unweighted automata)'))
        self.add_parm(frontend.CmdParm('evt_pairs', frontend.EVTPAIRS,
                                'e', 'set of event pairs'))

    def main(self, args):
        weighted_frontend.compute_shortest_path(args['comp_names'],
                                                args['req_names'],
                                                args['evt_pairs'])

if __name__ == '__main__':
    app = ComputeShortestPathApplication()
    app.run()

