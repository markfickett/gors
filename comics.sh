#!/bin/sh
# Check for comic updates and open web page if new
# Generalized to check for any image-based comic where the first image
# with a src=".." that follows a predictable form is the important update
# Uses various temporary files of the form [comicname][xyz]

# Written by Mark Fickett [ naib.webhop.org ]
# Last updated 2007 Oct 29

##### Configuration #####

# what command to use for opening URLs (${OPENCMD} ${COMICADDRESS})
OPENCMD='open'
# OPENCMD='firefox'

# Debug? (Any non-null value is 'false')
# prints out received/interpreted arguments, leaves reformatted html
# DEBUG='n'

##### Help text #####

# The regexp can get expanded when just by itself;
# let it, but remove spaces so it doesn't look like multiple arguments to test
if test -z `echo $3 | tr -d ' '`
then
	echo ""
	echo "Usage: comics.sh comicName comicPageURL ImageRegExp \\"
	echo "	[tag attribute] [occurenceNumber]"
	echo "For example,"
	echo "comics.sh qwantz http://qwantz.com \\"
	echo "	'http:\\/\\/www\\.qwantz\\.com\\/comics\\/comic.*\\.png'"
	echo "or"
	echo "comics.sh drmcninja http://drmcninja.com/ \\"
	echo "	'http:\/\/drmcninja\.com\/page\.php\?pageNum=.*\&issue=.*' \\"
	echo "	a href 2"
	echo ""
	echo "Various files of the form [comicname][xyz] will be used"
	echo "temporarily, and the file [comicname]old will be used to store"
	echo "the latest available image."
	echo ""
	exit
fi

##### Initial setup #####

# for unique storage of temporary data
COMICNAME=$1

# for fetching the page to look through
COMICADDRESS=$2

# a regexp which will match the source for the image of the most recent comic
COMICIMGRE=/$3/p

if test -z $4
then
	TAG=img
else
	TAG=$4
fi

if test -z $5
then
	ATTR=src
else
	ATTR=$5
fi

if test -z $6
then
	NUM=1
else
	NUM=$6
fi

if test -z ${DEBUG}
then
	echo comic name is: ${COMICNAME}
	echo comic address is: ${COMICADDRESS}
	echo comic image regexp, with added slashes and print flag, is:
	echo '	' ${COMICIMGRE}
	echo tag is: ${TAG}
	echo attribute is: ${ATTR}
	exit 0
fi

# Flag as in-progress
touch ${COMICNAME}going

##### Retreive, Compare, Open #####

if test -z ${DEBUG}
then
	echo ${COMICNAME}':	Checking...'
fi

COUNT=0
MAXRETRY=4
LIMIT=10
SECS=2
curl -s --show-error -o ${COMICNAME}html ${COMICADDRESS}
CURLEXIT=$?
if [ $CURLEXIT != 0 ]
then
	# RANDOM=random-`uname -s`-`uname -m`
	# //if [ ! -f $RANDOM ]
	# then
	#	cc random.c -o $RANDOM
	# fi
	while [ $CURLEXIT != 0 -a $COUNT -lt $MAXRETRY ]
	do
	#	SECS=`./${RANDOM} $LIMIT`
		echo Error from curl for $COMICNAME retry in $SECS sec.
		sleep $SECS
		curl -s --show-error -o ${COMICNAME}html ${COMICADDRESS}
		CURLEXIT=$?
		COUNT=`expr $COUNT + 1`
	done
	if [ $CURLEXIT != 0 ]
	then
		echo Error from curl for $COMICNAME $MAXRETRY times, dying.
		rm ${COMICNAME}going
		exit 1
	fi
fi

# Cull all original newlines (protect against img src="xy\nz")
# The below, with tr, broke due to choking on 'illegal byte sequence's
# cat ${COMICNAME}html | tr -d "\n" > ${COMICNAME}html2 2>/dev/null
# This sed is equivalent, using a sed function list
#	N to concatenate with the next line and embed the newline,
#	and then a substitution to remove the \n
sed '/x$/ { 
N 
s:x\n:x: 
}'< ${COMICNAME}html > ${COMICNAME}html2

# Add new newlines
sed -e 's/<'${TAG}'/\
<'${TAG}'/g' ${COMICNAME}html2 > ${COMICNAME}html
sed -e 's/>/>\
/g' ${COMICNAME}html > ${COMICNAME}html2
# Strip extra attributes
sed -e 's/<'${TAG}'.*'${ATTR}'/<'${TAG}' '${ATTR}'/g' ${COMICNAME}html2 > ${COMICNAME}html

# Right the files
# mv ${COMICNAME}html2 ${COMICNAME}html

# print only lines with the tag and the attribute,
#	cutting out all before the attribute [pipe to]
# cut out stuff after the close-quote (allow ' or " quotes)
sed -n -e "s/.*${TAG} ${ATTR}=[\"']//p" ${COMICNAME}html | \
	sed -n -e "s/[\"'].*//p" | sed -n ${COMICIMGRE} > ${COMICNAME}new

CURRENT=`sed -n ${NUM}p ${COMICNAME}new`
rm ${COMICNAME}new

if test -z ${DEBUG}
then
	echo ${COMICNAME}: current: ${CURRENT}
	exit;
fi

# clean up the html dump(s)
rm ${COMICNAME}html
# Since we change which of html/html2 is used, make this a test
if test -f ${COMICNAME}html2
then
	rm ${COMICNAME}html2
fi

if test -z ${CURRENT}
then
	echo 'Error in '${COMICNAME}': no match.'
	rm ${COMICNAME}going
	exit
fi

if test -e ${COMICNAME}old
then
	if test ${CURRENT} != `cat ${COMICNAME}old`
	then
		echo '     New '${COMICNAME}'!'
		echo ${CURRENT} > ${COMICNAME}old
		${OPENCMD} ${COMICADDRESS} &
		OPENRET=$?
		if [ $OPENRET != 0 ]
		then
			echo return value for $COMICNAME is $OPENRET
		fi
	else
		echo '  No new '${COMICNAME}'.'
	fi
else
	echo '  No old '${COMICNAME}'.'
	echo ${CURRENT} > ${COMICNAME}old
	${OPENCMD} ${COMICADDRESS} &
fi

# Remove in-progress flag
rm ${COMICNAME}going
