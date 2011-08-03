import logging
logging.basicConfig(
        format='[%(levelname)s %(name)s] %(message)s',
        level=logging.INFO)

import enum
import webbrowser, urllib2, xml, email, time, optparse, os
import plistlib

VERSION = (0, 1)
VERSION_STRING = '.'.join([str(v) for v in VERSION])

