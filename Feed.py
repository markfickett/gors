__all__ = [
	'Feed',
]

from Manifest import enum, webbrowser, \
	urllib2, xml, email, time, \
	logging
import email.utils
from xml.dom import minidom



class Feed:
	"""
	Store information about a feed, including URLs to check and to open,
	and timestamps of the latest available and viewed content.

	A Feed's log is a public field, so a Feed's owner can conveniently
	log messages under the Feed's name.

	Signals:
		updateFinished	an update has finished (succeeded or failed)
				argument is self (this Feed object)
	"""
	__SETTINGS = enum.Enum(
		'URL_RSS',
		'URL_OPEN',
		'OPENED',
		'CURRENT',
		'CHECKED',
	)
	def __init__(self, name):
		"""
		Create a new Feed with the given name.
		Initially all other data fields are None.
		"""
		self.__name = str(name)
		self.__rssURL = None
		self.__openURL = None
		self.__opened = None
		self.__current = None
		self.__checked = None	# double-precision seconds since epoch

		self.__error = None
		self.__updateThread = None

		self.log = logging.getLogger(self.__name)


	def getName(self):
		return self.__name


	def setRSSURL(self, url):
		"""Set the URL of the RSS feed, to check for updates."""
		newURL = str(url)
		if newURL != self.__rssURL:
			self.__rssURL = newURL
			self.__checked = None
			self.__current = None


	def setOpenURL(self, url):
		"""Set the URL to open (the address of the content to view)."""
		newURL = str(url)
		if newURL != self.__openURL:
			self.__openURL = newURL
			self.__opened = None


	def getError(self):
		"""Get a string error message, or None."""
		return self.__error


	def hasUnopened(self):
		"""
		Return whether an update has discovered content which
		has not yet been viewed.
		@see update, open
		"""
		return self.__current is not None \
			and self.__current != self.__opened


	def open(self):
		"""
		Open the OpenURL in a web browser. (Fall back to opening the
		RSS URL if not OpenURL is specified; fail with a log message
		if neither is specified.)
		"""
		if self.__openURL is None:
			openURL = self.__rssURL
		else:
			openURL = self.__openURL
		if openURL is None:
			self.log.error('cannot open: no URL')
			return

		webbrowser.open(openURL)
		self.__opened = self.__current


	def update(self):
		"""
		Check the RSS URL for the latest content. This runs the actual
		retrieval in a separate thread, and emits updateFinished when on
		completion (success or failure). (If an update thread is already
		in progress, do nothing.)
		"""
		if self.__rssURL is None:
			self.__error = 'cannot update: no RSS URL'
			self.log.error(self.__error)
			return

		if self.__updateThread is not None:
			return
		self.__updateThread = UpdateThread(self.__name, self.__rssURL)
		self.__updateThread.run()
		self.__updateThreadFinished()


	def __updateThreadFinished(self):
		err = self.__updateThread.getError()
		if err:
			self.__current = None
			self.__error = err
		else:
			self.__error = None
			self.__current = self.__updateThread.getCurrent()
		self.__updateThread = None
		self.__checked = time.time()


	def readSettings(self, settings):
		"""
		Read state from a QSettings object. This expects keys to be
		in the current group (so for multiple Feeds, the caller
		should begin/end a group around each).
		"""
		if settings.contains(self.__SETTINGS.URL_RSS):
			self.__rssURL = settings.getValue(
				self.__SETTINGS.URL_RSS)
		if settings.contains(self.__SETTINGS.URL_OPEN):
			self.__openURL = settings.getValue(
				self.__SETTINGS.URL_OPEN)
		if settings.contains(self.__SETTINGS.OPENED):
			self.__opened = settings.getValue(
				self.__SETTINGS.OPENED)
		if settings.contains(self.__SETTINGS.CURRENT):
			self.__current = settings.getValue(
				self.__SETTINGS.CURRENT)
		if settings.contains(self.__SETTINGS.CHECKED):
			d = settings.getFloatValue(
				self.__SETTINGS.CHECKED)
			if d is not None:
				self.__checked = d


	def writeSettings(self, settings):
		"""
		Write state to a QSettings object.
		@see readSettings
		"""
		if self.__rssURL is not None:
			settings.setValue(self.__SETTINGS.URL_RSS,
				self.__rssURL)
		if self.__openURL is not None:
			settings.setValue(self.__SETTINGS.URL_OPEN,
				self.__openURL)
		if self.__opened is not None:
			settings.setValue(self.__SETTINGS.OPENED,
				self.__opened)
		if self.__current is not None:
			settings.setValue(self.__SETTINGS.CURRENT,
				self.__current)
		if self.__checked is not None:
			settings.setValue(self.__SETTINGS.CHECKED,
				self.__checked)


	def __str__(self):
		"""Get a (multiline) string representation of this Feed."""
		info = [self.__name]

		info.append('URL for RSS: %s' % self.__rssURL)
		if self.__openURL is None and self.__rssURL is not None:
			info.append('URL to Open: None (will open RSS URL)')
		else:
			info.append('URL to Open: %s' % self.__openURL)

		label = 'Last Checked'
		if self.__checked is None:
			info.append('%s: Never' % label)
		else:
			info.append('%s: %s'
				% (label, time.ctime(self.__checked)))

		label = 'Latest Known Available'
		info.append('%s: %s' % (label, self.__current))

		label = '         Latest Opened'
		if self.hasUnopened():
			hasNew = ' (unopened)'
		else:
			hasNew = ''
		info.append('%s: %s%s' % (label,
			self.__opened,
			hasNew))

		return '\n\t'.join(info)



class UpdateThread:
	"""
	Retrieve the time of the latest content publication for an RSS feed
	by finding and interpreting the lastBuildDate channel attribute.

	Signals:
		updateFinished	update completed (success or failure)
	"""
	def __init__(self, name, rssURL):
		self.__rssURL = rssURL
		self.__error = None
		self.__current = None

		self.log = logging.getLogger(name)


	def run(self):
		self.__doUpdate()


	def __getFirstItemText(self, dom, name):
		"""
		Find the named attribute on the first item
		and return its text value.
		@return a tuple of (attributeText, errorMsg)
		"""
		elements = dom.getElementsByTagName(name)
		if not elements:
			error = ('error parsing: found no %s elements'
				% name)
			return None, error

		element = elements[0]
		textNode = element.firstChild

		if textNode is None \
		or textNode.nodeType != minidom.Node.TEXT_NODE:
			error = ('error parsing: expected text'
				+ ' as only child of %s') % name
			return None, error

		return str(textNode.data), None


	def __doUpdate(self):
		try:
			response = urllib2.urlopen(self.__rssURL)
		except urllib2.HTTPError, e:
			self.__error = str(e)
			self.log.error(self.__error, exc_info=True)
			return
		except urllib2.URLError, e:
			self.__error = e.reason.strerror
			self.log.error(self.__error, exc_info=True)
			return

		responseText = response.read()

		try:
			dom = minidom.parseString(responseText)
		except:
			self.__error = 'error parsing response as XML'
			self.log.error(self.__error, exc_info=True)
			return

		errorList = []
		text, error = self.__getFirstItemText(dom, 'guid')
		if text is None:
			errorList.append(error)
			text, error = self.__getFirstItemText(dom, 'pubDate')
		if text is None:
			errorList.append(error)
			text, error = self.__getFirstItemText(dom, 'published')
		if text is None:
			errorList.append(error)
			errorMsg = ' and '.join(errorList)
			self.__error = errorMsg
			self.log.error(errorMsg)
			return

		self.__current = text
		self.log.debug('found current: %s' % self.__current)


	def getError(self):
		"""Get a string error message, or None."""
		return self.__error


	def getCurrent(self):
		"""Get the value of the lastBuildTime field as a double."""
		return self.__current



