Mark Fickett [ naib.webhop.org ]
Last updated 2008 September 21

This system is meant to check for updates in webcomics (or other web pages) and open the web site for viewing if there is an update.

Usage: comics [comicnames ...]
	comics is something that runs comics/main.sh
	comicnames are whitespace-separated names of comics from comics.conf

An example of how it looks from  the command line:
$ comics
  No new drmcninja.
Error in flakypastry: no match.
  No new scarygoround.
  No new ddoi.
  No new qc.
  No new catandgirl.
     New bunny!
     New qwantz!
     New gc!
  No new postsecret.
  No old shortpacked.
     New dooce!
  No old wondermark.

Another example invocation might be:
# comics qc gc
  No new qc.
     New gc!

(A source checked for the first time opens by default with the 'No old' message. An updated source opens in the default web browser with the 'New .. !' message. An error can occur with an HTTP timeout or a bad regular expression. A source that hasn't been updated results in the 'No new' message.)

Run main.sh to check comics. (Double-clicking and invocation from other directories is supported.) If arguments are supplied to main.sh, only the given comics are checked. (I have "alias comics='code/comics/main.sh'" in my shell init file.)

Edit comics.conf with new comic names, comic URLs, and comic image regular expressions to add new checks. Each unique comic name will have a [comicname]old file to store the latest retreived comic image URL.

If you come across a comic for which the html pre-processing is insufficient (and the image URL is therefore unretreivable), let me know what needs to be done! If you comment out the DEBUG='n' line (with #), [comicname]html will be left available for perusal as the pre-processed html.

There is some duplication of effort with RSS, however I find this more convenient, and the workflow I want (if new, open latest in web browser) is something I have not found in an RSS client. Also, since the retreived data for the status check is the HTML only, this is likely not a greater drain on server resources.

Linux is easily supported by editing comics.sh and setting OPENCMD='firefox' - that is, making firefox the comman used to open URLs of updated comics.

Bugs: The HTML tags specified are case-sensitive.
