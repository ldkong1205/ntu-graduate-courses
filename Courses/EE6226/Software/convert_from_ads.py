#!/usr/bin/env python
# $Id: convert_from_ads.py 538 2009-11-09 14:51:19Z hat $
"""
Convert an automaton in ADS format to the format used by this package.
"""
import sys
# Make sure the installed version is used (is in the Python path).
site_packages = "%SITEPACKAGES%"
if not site_packages.startswith("%SITE") and site_packages not in sys.path:
    # Installed version, prefix installed path.
    sys.path = [site_packages] + sys.path


from automata import frontend

class ConvertFromADSApplication(frontend.Application):
    def __init__(self):
        cmd = 'convert_from_ads'
        desc = 'Convert an automaton from the ADS format.'
        frontend.Application.__init__(self, cmd, desc)

    def add_options(self):
        self.add_parm(frontend.CmdParm('ads_name', frontend.EXIST_ADS,
                                       'i<', 'ads-file'))
        self.add_parm(frontend.CmdParm('aut_name', frontend.AUT,
                                       'o>', 'destination automaton filename'))

    def main(self, args):
        frontend.convert_from_ads(args['ads_name'], args['aut_name'])

if __name__ == '__main__':
    app = ConvertFromADSApplication()
    app.run()

