#!/usr/bin/env python
# $Id: make_language_equivalence_test.py 538 2009-11-09 14:51:19Z hat $
"""
Check whether two automata recognize the same language.
"""
import sys
# Make sure the installed version is used (is in the Python path).
site_packages = "%SITEPACKAGES%"
if not site_packages.startswith("%SITE") and site_packages not in sys.path:
    # Installed version, prefix installed path.
    sys.path = [site_packages] + sys.path


from automata import frontend

class TestLanguageEquivalenceApplication(frontend.Application):
    def __init__(self):
        cmd = 'make_language_equivalence_test'
        desc = 'Check whether two automata recognize the same language.'
        frontend.Application.__init__(self, cmd, desc)

    def add_options(self):
        self.add_parm(frontend.CmdParm('aut1_name', frontend.EXIST_AUT,
                                       'i+', 'first model'))
        self.add_parm(frontend.CmdParm('aut2_name', frontend.EXIST_AUT,
                                       'i+', 'second model'))

    def main(self, args):
        frontend.make_language_equivalence_test(args['aut1_name'],
                                                args['aut2_name'])

if __name__ == '__main__':
    app = TestLanguageEquivalenceApplication()
    app.run()

