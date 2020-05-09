#!/usr/bin/env python
# $Id: generate_task_resource_use.py 552 2009-11-19 12:14:16Z hat $
"""
Generate a task/resource usage list for a given path.
"""
import sys
# Make sure the installed version is used (is in the Python path).
site_packages = "%SITEPACKAGES%"
if not site_packages.startswith("%SITE") and site_packages not in sys.path:
    # Installed version, prefix installed path.
    sys.path = [site_packages] + sys.path


from automata import frontend, weighted_frontend

class GenerateTaskResourceUseApplication(frontend.Application):
    def __init__(self):
        cmd = 'generate_task_resource_use'
        desc = 'Generate a task/resource usage list for a given path.'
        frontend.Application.__init__(self, cmd, desc)

    def add_options(self):
        self.add_parm(frontend.CmdParm('comp_names', frontend.AUTLIST, 'p+',
                                    'list of components (weighted automata)'))
        self.add_parm(frontend.CmdParm('req_names', frontend.AUTLIST, 'r+',
                                'list of requirements (unweighted automata)'))
        self.add_parm(frontend.CmdParm('path', frontend.AUT,
                                       '', 'sequence of events'))
        self.add_parm(frontend.CmdParm('plot_names', frontend.AUTLIST,
                               '', 'Automata to plot (leave empty for all)'))
        self.add_parm(frontend.CmdParm('use_name', frontend.AUT,
                                       's>', 'filename with use of resources'))

    def main(self, args):
        weighted_frontend.generate_task_resource_use(args['comp_names'],
                                                     args['req_names'],
                                                     args['path'],
                                                     args['plot_names'],
                                                     args['use_name'])

if __name__ == '__main__':
    app = GenerateTaskResourceUseApplication()
    app.run()

