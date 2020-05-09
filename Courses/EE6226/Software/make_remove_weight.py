#!/usr/bin/env python
# $Id: make_remove_weight.py 538 2009-11-09 14:51:19Z hat $
"""
Remove weights of a weighted automaton.
"""
import sys
# Make sure the installed version is used (is in the Python path).
site_packages = "%SITEPACKAGES%"
if not site_packages.startswith("%SITE") and site_packages not in sys.path:
    # Installed version, prefix installed path.
    sys.path = [site_packages] + sys.path


from automata import frontend, weighted_frontend

class RemoveWeightsApplication(frontend.Application):
    def __init__(self):
        cmd = 'make_remove_weight'
        desc = 'Remove weights of a weighted automaton.'
        frontend.Application.__init__(self, cmd, desc)

    def add_options(self):
        self.add_parm(frontend.CmdParm('aut_name', frontend.EXIST_AUT,
                                       'i<', 'weighted automaton'))
        self.add_parm(frontend.CmdParm('result_name', frontend.AUT,
                                       'o>', 'unweighted automaton'))

    def main(self, args):
        weighted_frontend.make_remove_weighted(args['aut_name'],
                                               args['result_name'])

if __name__ == '__main__':
    app = RemoveWeightsApplication()
    app.run()

