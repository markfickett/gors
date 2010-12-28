__all__ = [
	'Feed',
]

from Manifest import QtCore, enum, webbrowser, \
	urllib2, xml, email, time, \
	logging, urllib, getpass
import email.utils
from xml.dom import minidom



class Feed(QtCore.QObject):
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
		'AUTH_USERNAME',
	)
	def __init__(self, name):
		"""
		Create a new Feed with the given name.
		Initially all other data fields are None.
		"""
		QtCore.QObject.__init__(self)
		self.__name = str(name)
		self.__rssURL = None
		self.__openURL = None
		self.__opened = None
		self.__current = None
		self.__authUsername = None	# implies basic HTTP auth
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


	def setUsername(self, username):
		"""
		Set a username, which will cause basic HTTP authentication
		to be used; the password will be prompted for at urlopen time.
		(Assume a change in username affects data retrieved.)
		"""
		newUsername = str(username)
		if self.__authUsername != newUsername:
			self.__authUsername = newUsername
			self.__checked = None
			self.__current = None


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
			self.__emitUpdateFinished()
			return

		if self.__updateThread is not None:
			return
		self.__updateThread = UpdateThread(self.__name, self.__rssURL,
			username=self.__authUsername)
		self.connect(self.__updateThread,
			QtCore.SIGNAL('updateFinished'),
			self.__updateThreadFinished)
		self.__updateThread.start()


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


		self.__emitUpdateFinished()


	def __emitUpdateFinished(self):
		self.emit(QtCore.SIGNAL('updateFinished'), self)


	def readSettings(self, settings):
		"""
		Read state from a QSettings object. This expects keys to be
		in the current group (so for multiple Feeds, the caller
		should begin/end a group around each).
		"""
		if settings.contains(str(self.__SETTINGS.URL_RSS)):
			self.__rssURL = str(settings.value(
				str(self.__SETTINGS.URL_RSS)).toString())
		if settings.contains(str(self.__SETTINGS.URL_OPEN)):
			self.__openURL = str(settings.value(
				str(self.__SETTINGS.URL_OPEN)).toString())
		if settings.contains(str(self.__SETTINGS.OPENED)):
			qv = settings.value(str(self.__SETTINGS.OPENED))
			self.__opened = str(qv.toString())
		if settings.contains(str(self.__SETTINGS.CURRENT)):
			qv = settings.value(str(self.__SETTINGS.CURRENT))
			self.__current = str(qv.toString())
		if settings.contains(str(self.__SETTINGS.CHECKED)):
			d, ok = settings.value(
				str(self.__SETTINGS.CHECKED)).toDouble()
			if ok:
				self.__checked = d
		if settings.contains(str(self.__SETTINGS.AUTH_USERNAME)):
			qv = settings.value(str(self.__SETTINGS.AUTH_USERNAME))
			self.__authUsername = str(qv.toString())


	def writeSettings(self, settings):
		"""
		Write state to a QSettings object.
		@see readSettings
		"""
		if self.__rssURL is not None:
			settings.setValue(str(self.__SETTINGS.URL_RSS),
				QtCore.QVariant(QtCore.QString(self.__rssURL)))
		if self.__openURL is not None:
			settings.setValue(str(self.__SETTINGS.URL_OPEN),
				QtCore.QVariant(QtCore.QString(self.__openURL)))
		if self.__opened is not None:
			settings.setValue(str(self.__SETTINGS.OPENED),
				QtCore.QVariant(self.__opened))
		if self.__current is not None:
			settings.setValue(str(self.__SETTINGS.CURRENT),
				QtCore.QVariant(self.__current))
		if self.__checked is not None:
			settings.setValue(str(self.__SETTINGS.CHECKED),
				QtCore.QVariant(self.__checked))
		if self.__authUsername is not None:
			settings.setValue(str(self.__SETTINGS.AUTH_USERNAME),
				QtCore.QVariant(QtCore.QString(
					self.__authUsername)))


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
		if self.__authUsername is not None:
			info.append('Authenticate for "%s"'
				% self.__authUsername)

		return '\n\t'.join(info)



class PasswordPromptingOpener(urllib.FancyURLopener):
	"""
	Open a URL with basic HTTP authentication,
	prompting for password but having username set beforehand.
	"""
	def __init__(self, username):
		urllib.FancyURLopener.__init__(self)
		self.__username = str(username)

	def prompt_user_passwd(self, host, realm):
		password = getpass.getpass('Password for %s@%s (%s): '
			% (self.__username, host, realm))
		return (self.__username, password)



class UpdateThread(QtCore.QThread):
	"""
	Retrieve the time of the latest content publication for an RSS feed
	by finding and interpreting the lastBuildDate channel attribute.

	Signals:
		updateFinished	update completed (success or failure)
	"""
	def __init__(self, name, rssURL, username=None):
		QtCore.QThread.__init__(self)
		self.__rssURL = rssURL
		self.__error = None
		self.__current = None
		self.__username = username

		self.log = logging.getLogger(name)


	def run(self):
		self.__doUpdate()
		# TODO why does finishing execution of run not emit finished?
		self.emit(QtCore.SIGNAL('updateFinished'))


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


	def __getPubDate(self, dom):
		"""
		Get the first item's pubDate attribute
		as double seconds since the epoch.
		"""
		dateText, error = self.__getFirstItemText(dom, 'pubDate')
		if dateText is None:
			return None, error

		parsedDateTuple = email.utils.parsedate_tz(dateText)
		if not parsedDateTuple:
			error = ("error parsing '%s' as date" % dateText)
			return None, error

		try:
			doubleTime = email.utils.mktime_tz(parsedDateTuple)
		except:
			error = ("error building time value"
				+ " from parsed date '%s'") % dateText
			return None, error

		return doubleTime, None


	def __doUpdate(self):
		try:
			if self.__username is not None:
				# Use FancyURLopener instead of
				# urllib2.HTTPBasicAuthHandler so that realm
				# and uri do not have to be set beforehand.
				authOpener = PasswordPromptingOpener(
					self.__username)
				response = authOpener.open(self.__rssURL)
			else:
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

		text, error = self.__getFirstItemText(dom, 'guid')
		if text is None:
			text, error = self.__getFirstItemText(dom, 'pubDate')
		if text is None: # atom feed
			text, error = self.__getFirstItemText(dom, 'issued')
		if text is None:
			self.__error = error
			self.log.error(error)
			return

		self.__current = text
		self.log.debug('found current: %s' % self.__current)


	def getError(self):
		"""Get a string error message, or None."""
		return self.__error


	def getCurrent(self):
		"""Get the value of the lastBuildTime field as a double."""
		return self.__current



