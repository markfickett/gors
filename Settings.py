from Manifest import plistlib, logging, os

log = logging.getLogger('Settings')


class Settings:
	__SETTINGS_DIR = '~/Library/Preferences/'
	__DELIMITER = '.'
	"""
	Settings/preferences, to encapsulate storing latest-read information
	in a MacOS X .plist. (Compatible with QSettings' file format on OS X.)
	"""
	def __init__(self, domain='com.markfickett.gors'):
		"""
		Create a new Settings, reading from a default location
		for the given domain (~/Library/Preferences/%s.plist).
		"""
		settingsDir = os.path.expanduser(self.__SETTINGS_DIR)
		if not os.path.isdir(settingsDir):
			os.makedirs(settingsDir)
		self.__settingsFileName = os.path.join(settingsDir,
			domain + '.plist')
		if os.path.isfile(self.__settingsFileName):
			self.__settings = plistlib.readPlist(
				self.__settingsFileName)
		else:
			self.clear()
		self.__currentGroupNames = []


	def clear(self):
		self.__settings = {}


	def getFileName(self):
		return self.__settingsFileName


	def _pushGroup(self, groupName):
		"""
		For use by GroupGuard: push a name onto the group-name stack.
		"""
		self.__currentGroupNames.append(groupName)


	def _popGroup(self):
		"""
		For use by GroupGuard: pop a name off of the group-name stack,
		and return the popped name.
		"""
		return self.__currentGroupNames.pop()


	class _GroupGuard:
		def __init__(self, settings, groupName):
			self.__settings = settings
			self.__groupName = str(groupName)
		def __enter__(self):
			self.__settings._pushGroup(self.__groupName)
		def __exit__(self, type, value, traceback):
			exitedGroup = self.__settings._popGroup()
			if exitedGroup != self.__groupName:
				log.error(("exited group '%s' did not match"
				+ " GroupGuard's group '%s'")
				% (exitedGroup, self.__groupName))


	def groupGuard(self, groupNameRaw):
		"""
		Create and return a GroupGuard for this Settings object,
		which prepends a group name to all settings names referenced
		while it is active.
		"""
		groupName = str(groupNameRaw)
		if self.__DELIMITER in groupName:
			raise ValueError(("Illegal group name '%s' contains"
			+ " delimiter '%s'.") % (groupName, self.__DELIMITER))
		return self._GroupGuard(self, groupName)


	def getChildGroups(self):
		"""
		Return a list of all groups under the current group.
		(This is potentially slow, as it recomputes every time.)
		"""
		groupPrefix = self.__DELIMITER.join(self.__currentGroupNames)
		if groupPrefix:
			groupPrefix += self.__DELIMITER
		skipLen = len(groupPrefix)
		childGroups = set()
		for keyName in self.__settings.keys():
			if keyName.startswith(groupPrefix):
				childKey = keyName[skipLen:]
				groupKey, _, grandChildKey = \
					childKey.partition(self.__DELIMITER)
				if grandChildKey:
					childGroups.add(groupKey)
		return filter(bool, childGroups)


	def __getKey(self, keyNameRaw, extant=True):
		"""
		Get the full name of the given keyName under the current group.
		If extant is True, only return extant keys;
			otherwise return None.
		"""
		fullKeyName = self.__DELIMITER.join(
			self.__currentGroupNames + [str(keyNameRaw)])
		if extant and (fullKeyName not in self.__settings):
			return None
		return fullKeyName


	def contains(self, keyName):
		return self.__getKey(str(keyName)) is not None


	def getValue(self, keyNameLocal):
		keyName = self.__getKey(keyNameLocal)
		if keyName is None:
			keyName = self.__getKey(keyNameLocal, extant=False)
			raise ValueError("No such key: '%s' ('%s')."
			% (keyNameLocal, keyName))
		return self.__settings[keyName]


	def getFloatValue(self, keyName):
		"""or None"""
		v = self.getValue(keyName)
		try:
			return float(v)
		except ValueError, e:
			log.warning("Could not parse '%s' as float for '%s': %s"
				% (v, self.__getKey(keyName), e.message))
			return None


	def setValue(self, keyNameLocal, value):
		keyName = self.__getKey(keyNameLocal, extant=False)
		self.__settings[keyName] = str(value)


	def write(self):
		try:
			plistlib.writePlist(self.__settings,
				self.__settingsFileName)
			log.debug("Saved settings to '%s'."
				% self.__settingsFileName)
		except:
			log.error(("Error writing settings to '%s'."
			+ " Settings data is:\n%s\n")
			% (self.__settingsFileName, self.__settings))
			raise


