#!/usr/bin/env python
# $Id: make_product.py 573 2010-01-07 09:44:19Z hat $
"""
Compute the product of two automata.
"""
import sys
# Make sure the installed version is used (is in the Python path).
site_packages = "%SITEPACKAGES%"
if not site_packages.startswith("%SITE") and site_packages not in sys.path:
    # Installed version, prefix installed path.
    sys.path = [site_packages] + sys.path


from automata import frontend

class MakeProductApplication(frontend.Application):
    def __init__(self):
        cmd = 'make_product'
        desc = 'Compute the product of two or more automata.'
        frontend.Application.__init__(self, cmd, desc)

    def add_options(self):
        self.add_parm(frontend.CmdParm('aut_names', frontend.AUTLIST, '+i',
                                       'list of your input automata'))

        self.add_parm(frontend.CmdParm('product_name', frontend.AUT, '-o>',
                                       'product automaton'))

    def main(self, args):
        frontend.make_product(args['aut_names'], args['product_name'],
                              preserve_names = True)

if __name__ == '__main__':
    app = MakeProductApplication()
    app.run()
