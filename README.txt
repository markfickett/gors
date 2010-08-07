Check for updates to web sites' RSS feeds and, in response, open the main web site. This is meant for sites which present content in a more pleasing way than does an RSS reader; and for users who wish to keep all content in the web browser in favor of adding alternate viewers.

The name 'gors' is derived from 'Go RSS', and is pronounced like the gorse bush.

The implementation is in Python and requires:
	PyQt: http://www.riverbankcomputing.co.uk/software/pyqt/download
	enum (single file Python package): http://pypi.python.org/pypi/enum/

As of 2010 August, my (Mark Fickett's) intent is to write a menu bar (or system tray) version; otherwise the Qt dependency would have been avoided. (However, with that planned, Qt's signals and threads were convenient.) (Version 0.1 is the original shell script implementation.)


Example Usage (run gors --help for more):

Check all feeds:
$ gors
[INFO asofterworld] no update
[INFO ddoi] new: opening
[INFO bigpicture] no update
[INFO samandfuzzy] no update
[INFO visualnotes] new: opening
[INFO xkcd] new: opening

Check only named feeds:
$ gors ddoi
[INFO ddoi] new: opening

Add a new feed:
$ gors --add 3ps --open-url http://www.threepanelsoul.com/index.php --rss-url http://www.rsspect.com/rss/threeps.xml
(Note that services such as rsspect.com and feed43.com can be used to create feeds for web sites which do not have RSS feeds.)


Implementation

When invoked, gors requests that each of the objects representing feeds check for updates. Each feed object starts a new thread which fetches the RSS feed's source, parses the returned XML, and stores the latest available item's guid attribute; the feed object then notifies gors (via Qt signal). For any updated feeds, gors opens the main URL in the OS-designated web browser.

