#!/usr/bin/env python
# $Id: make_weighted_product.py 538 2009-11-09 14:51:19Z hat $
"""
Compute the weighted product of several automata.
"""
import sys
# Make sure the installed version is used (is in the Python path).
site_packages = "%SITEPACKAGES%"
if not site_packages.startswith("%SITE") and site_packages not in sys.path:
    # Installed version, prefix installed path.
    sys.path = [site_packages] + sys.path


from automata import frontend, weighted_frontend

class MakeWeightedProductApplication(frontend.Application):
    def __init__(self):
        cmd = 'make_weighted_product'
        desc = 'Compute the weighted product of several automata.'
        frontend.Application.__init__(self, cmd, desc)

    def add_options(self):
        self.add_parm(frontend.CmdParm('aut_names', frontend.AUTLIST,
                                       'i+<', 'input weighted automata'))
        self.add_parm(frontend.CmdParm('product_name', frontend.AUT,
                                       'o>', 'product automaton'))

    def main(self, args):
        weighted_frontend.make_weighted_product(args['aut_names'],
                                                args['product_name'])

if __name__ == '__main__':
    app = MakeWeightedProductApplication()
    app.run()

