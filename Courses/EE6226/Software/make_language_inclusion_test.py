#!/usr/bin/env python
# $Id: make_language_inclusion_test.py 538 2009-11-09 14:51:19Z hat $
"""
Check whether the 'small' language is contained in the 'big' language.
"""
import sys
# Make sure the installed version is used (is in the Python path).
site_packages = "%SITEPACKAGES%"
if not site_packages.startswith("%SITE") and site_packages not in sys.path:
    # Installed version, prefix installed path.
    sys.path = [site_packages] + sys.path


from automata import frontend

class TestLanguageInclusionApplication(frontend.Application):
    def __init__(self):
        cmd = 'make_language_inclusion_test'
        desc = "Check whether the 'small' language is contained in the " \
               "'big' language."
        frontend.Application.__init__(self, cmd, desc)

    def add_options(self):
        self.add_parm(frontend.CmdParm('small', frontend.EXIST_AUT,
                                       'i+s', 'first (smallest) model'))
        self.add_parm(frontend.CmdParm('big', frontend.EXIST_AUT,
                                       'i+b', 'second (biggest) model'))

    def main(self, args):
        frontend.make_language_inclusion_test(args['small'], args['big'])

if __name__ == '__main__':
    app = TestLanguageInclusionApplication()
    app.run()

