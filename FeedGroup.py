__all__ = [
	'FeedGroup',
]

from Manifest import logging
from Feed import Feed

log = logging.getLogger('gors')



class FeedGroup:
	"""
	Manage Feeds. Provide encapsulation for updating, opening,
	and reading and writing them to/from QSettings in bulk.
	"""
	__SETTINGS_FEEDS = 'feeds'
	def __init__(self):
		self.__feeds = []
		self.__feedsUpdatingSet = set()


	def addFeed(self, feed):
		"""
		Add a Feed to this group. Once added, when a feed emits
		updateFinished, the group will automatically open new content.
		"""
		self.__feeds.append(feed)


	def getFeed(self, feedName):
		"""Get a feed by name, or None."""
		for feed in self.__feeds:
			if feed.getName() == feedName:
				return feed
		return None


	def getFeeds(self, feedNames=None):
		"""Get a list of all this group's Feeds."""
		return self.__filterFeeds(feedNames)


	def removeFeed(self, feed):
		"""
		Remove the given Feed from this group.
		Disconnect from updateFinished.
		"""
		if feed not in self.__feeds:
			raise ValueError("Feed '%s' not a group member. (%s)"
				% (feed.getName(), feed))
		self.__feeds.remove(feed)


	def __filterFeeds(self, feedNames):
		if feedNames is None:
			feeds = self.__feeds
		else:
			feeds = []
			names = set(feedNames)
			for feed in self.__feeds:
				if feed.getName() in names:
					names.remove(feed.getName())
					feeds.append(feed)
			if names:
				log.warning('unrecognized feeds ignored: %s'
				% feedNames)
		return feeds


	def update(self, feedNames=None):
		"""
		Update feeds (and open new content when updates finish).
		@param feedNames: a list of feed names, limiting which to update
			(may be any object supporting 'in')
		"""
		for feed in self.__filterFeeds(feedNames):
			self.__feedsUpdatingSet.add(feed)
			feed.update()
			self.__feedUpdateFinished(feed)


	def hasFeedsUpdating(self):
		"""
		Return whether any Feeds have started updating
		but which have not yet reported finishing.
		"""
		return bool(self.__feedsUpdatingSet)


	def getUpdatingFeedNames(self):
		"""
		Return a list of names of Feeds which have started updating
		but which have not yet reported finishing.
		"""
		return [f.getName() for f in self.__feedsUpdatingSet]


	def __feedUpdateFinished(self, feed):
		if feed in self.__feedsUpdatingSet:
			self.__feedsUpdatingSet.remove(feed)
		if feed.hasUnopened():
			feed.log.info('new: opening')
			feed.open()
		elif not feed.getError():
			feed.log.info('no update')


	def readSettings(self, settings):
		"""
		Read Feeds from a QSettings object.
		Feeds are read from a 'feeds' group under the current group,
		and each subgroup of the 'feeds' group is taken as a Feed name.
		"""
		with settings.groupGuard(self.__SETTINGS_FEEDS):
			groupNames = settings.getChildGroups()
			for groupName in groupNames:
				feed = Feed(groupName)
				with settings.groupGuard(groupName):
					feed.readSettings(settings)
				self.addFeed(feed)
		log.debug('Loaded feeds: %s'
			% [f.getName() for f in self.__feeds])


	def writeSettings(self, settings):
		"""
		Write Feeds to the given QSettings object.
		@see readSettings
		"""
		with settings.groupGuard(self.__SETTINGS_FEEDS):
			for feed in self.__feeds:
				with settings.groupGuard(feed.getName()):
					feed.writeSettings(settings)



