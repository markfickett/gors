"""
Check for updates to web sites via RSS, and open new content.
"""

from Manifest import QtCore, time, logging, optparse
import Manifest
log = logging.getLogger('gors')

parser = optparse.OptionParser(
	usage="""%prog

Update all feeds and open all new content, or only named feeds:
  %prog [NAME ...]
Add a new feed:
  %prog --add NAME --rss-url URL --open-url URL
Remove a feed:
  %prog --delete NAME
List information about all or only named feeds:
  %prog --list [NAME ...]""",
	version='%%prog %s' % Manifest.VERSION_STRING,
)
parser.add_option('-v', '--verbose', action='store_true')

addGroup = optparse.OptionGroup(parser, 'Add A Feed')
addGroup.add_option('-a', '--add', metavar='NAME',
	help='Add a feed, giving its name as an argument.')
addGroup.add_option('--rss-url', dest='rssurl', metavar='URL',
	help='Specify the RSS URL for a new feed.')
addGroup.add_option('--open-url', dest='openurl', metavar='URL',
	help=('Specify the URL to open for a new feed. This is the address'
		+ ' opened in a web browser when new content is available.'))
addGroup.add_option('--username', dest='username', metavar='USERNAME',
	help=('Specify a username for basic HTTP authentication. A password '
		+ 'prompt will be presented when the RSS url is retrieved.'))
parser.add_option_group(addGroup)

deleteGroup = optparse.OptionGroup(parser, 'Delete A Feed')
deleteGroup.add_option('-d', '--delete', metavar='NAME',
	help='Delete a feed, specified by name.')
parser.add_option_group(deleteGroup)

listGroup = optparse.OptionGroup(parser, 'List Feeds')
listGroup.add_option('-l', '--list', action='store_true',
	help=('List information about known feeds (after any'
		+ ' additions/removals). Optionally specify for which feeds'
		+ ' to list information.'))
parser.add_option_group(listGroup)

options, args = parser.parse_args()

if options.verbose:
	logging.getLogger().setLevel(logging.DEBUG)

from FeedGroup import FeedGroup
from Feed import Feed

# An application processing events is required for signals.
app = QtCore.QCoreApplication([])

QtCore.QCoreApplication.setOrganizationDomain('markfickett')
QtCore.QCoreApplication.setOrganizationName('markfickett')
QtCore.QCoreApplication.setApplicationName('gors')

settings = QtCore.QSettings()
log.debug("settings file is '%s'" % str(settings.fileName()))

feedGroup = FeedGroup()
feedGroup.readSettings(settings)

doUpdate = not any([options.add, options.delete, options.list])
if not (doUpdate or options.list) and args:
	parser.error(('positional arguments legal only when updating'
		+ ' or listing (with --list): %s')
		% args)

if options.add:
	if not options.rssurl:
		parser.error('--add requires --rss-url')
	if not options.openurl:
		log.warning(("new feed '%s' will open the RSS URL "
			+ "(use --open-url to specify a different URL to open")
			% options.rssurl)
	feed = Feed(options.add)
	feed.setRSSURL(options.rssurl)
	if options.openurl:
		feed.setOpenURL(options.openurl)
	if options.username:
		feed.setUsername(options.username)
	feedGroup.addFeed(feed)
if options.delete:
	feed = feedGroup.getFeed(options.delete)
	if not feed:
		parser.error("not found: '%s'" % options.delete)
	feedGroup.removeFeed(feed)
if options.list:
	kwargs = {}
	if args:
		kwargs['feedNames'] = args
	for feed in feedGroup.getFeeds(**kwargs):
		log.info(feed)

if doUpdate:
	kwargs = {}
	if args:
		kwargs['feedNames'] = args
	feedGroup.update(**kwargs)

	elapsed = 0
	interval = 1
	while feedGroup.hasFeedsUpdating():
		if elapsed > 10 and elapsed % 5 == 0:
			log.info('waiting for: %s'
				% ', '.join(feedGroup.getUpdatingFeedNames()))
		time.sleep(interval)
		elapsed += interval
		app.processEvents()

feedGroup.writeSettings(settings)

