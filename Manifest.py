import logging
logging.basicConfig(
        format='[%(levelname)s %(name)s] %(message)s',
        level=logging.INFO)

import QtUtil
from QtUtil.Manifest import QtCore, QtGui
import enum
import webbrowser, urllib2, xml, email, time, optparse

VERSION = (0, 1)
VERSION_STRING = '.'.join([str(v) for v in VERSION])

