#!/bin/sh
# Check for comic updates and open web page if new
# Generalized from checking for any image-based comic where the important update
# is the first image with a src="something" that follows a predictable form.
# Uses various temporary files of the form [comicname][xyz]

# Written by Mark Fickett [ naib.webhop.org ]
# Last updated 2008 March 09

##### Configuration #####

# what command to use for opening URLs (${OPENCMD} ${COMICADDRESS})
OPENCMD='open'
# OPENCMD='firefox'

# Debug? (Any non-null value is 'false')
# prints out received/interpreted arguments, leaves reformatted html
DEBUG='n'

##### Help text #####

function printHelpAndExit() {
cat - <<EOF
Argumens:
	-n
	--name comicName (required)
	-u
	--url comicPageURL (required)
	-r
	--regexp ImageRegExp (required)
	-t
	--tag tag (optional, default is img)
	-a
	--attribute attribute (optional, default is src)
	-N
	--occurence occurenceNumber (optional, default is 1)
	-o
	--openattribute (optional, default is false)
For example:
	comics.sh --name qwantz --url http://qwantz.com \\
		'http:\\/\\/www\\.qwantz\\.com\\/comics\\/comic.*\\.png'
	or
	comics.sh drmcninja http://drmcninja.com/ \\
		'http:\/\/drmcninja\.com\/page\.php\?pageNum=.*\&issue=.*' \\
		a href 2
Various files of the form [comicname][xyz] will be used
	temporarily, and the file cache/[comicname]old will be used to store
	the url (attribute value) of the latest available image (or other item).
EOF
	echo Original call was: $*
	exit 1
}

##### Argument Parsing #####

# for unique storage of temporary data
COMICNAME=''
# for fetching the page to look through
COMICADDRESS=''
# a regexp which will match the source for the image of the most recent comic
COMICIMGRE=''

# what tag to look for
TAG=img
# what attribute to look for, in the tag
ATTR=src
# what ordinal occurance of the tag to look for
NUM=1
# if set, open the retrived attribute value, rather than the COMICADDRESS
# OPENATTRIBUTE

while [ $# -gt 0 ]
do
	# All arguments require an argument, except "--openattribute"
	if [ \( $# -lt 2 \) -a \( $1 != "--openattribute" \) ]
	then
		echo Error during argument parsing at
		echo argc=$#
		echo 1=$1
		echo 2=$2
		printHelpAndExit $0 $*
	fi

	case $1 in
	"--name" | "-n" )
		COMICNAME=$2
		shift
		;;
	"--url" | "-u" )
		COMICADDRESS=$2
		shift
		;;
	"--regexp" | "-r" )
		COMICIMGRE=/$2/p
		shift
		;;
	"--tag" | "-t" )
		TAG=$2
		shift
		;;
	"--attribute" | "-a" )
		ATTR=$2
		shift
		;;
	"--occurence" | "-N" )
		NUM=$2
		shift
		;;
	"--openattribute" | "-o" )
		OPENATTRIBUTE="YES"
		;;
	* )
		echo "Unrecognized or misplaced argument: " $1
		printHelpAndExit $0 $*
		;;
	esac
	shift
done

if [ -z "$COMICNAME" ]
then
	echo "Required argument --name not given"
	printHelpAndExit $0 $*
elif [ -z "$COMICADDRESS" ]
then
	echo "Required argument --url not given"
	printHelpAndExit $0 $*
elif [ -z "$COMICIMGRE" ]
then
	echo "Required argument --regexp not given"
	printHelpAndExit $0 $*
	
fi

if test -z ${DEBUG}
then
	echo comic name is: ${COMICNAME}
	echo comic address is: ${COMICADDRESS}
	echo comic image regexp, with added slashes and print flag, is:
	echo '	' ${COMICIMGRE}
	echo tag is: ${TAG}
	echo attribute is: ${ATTR}
	if [ "$OPENATTRIBUTE" ]
	then
		echo openattribute is yes
	else
		echo openattribute is no
	fi
	exit 0
fi

##### Initial setup #####

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
	echo Debug exit: leaving ${COMICNAME}going
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

if test -e cache/${COMICNAME}old
then
	if test ${CURRENT} != `cat cache/${COMICNAME}old`
	then
		echo '     New '${COMICNAME}'!'
		echo ${CURRENT} > cache/${COMICNAME}old
		if [ "${OPENATTRIBUTE}" ]
		then
			${OPENCMD} ${CURRENT} &
		else
			${OPENCMD} ${COMICADDRESS} &
		fi
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
	echo ${CURRENT} > cache/${COMICNAME}old
	if [ "${OPENATTRIBUTE}" ]
	then
		${OPENCMD} ${CURRENT} &
	else
		${OPENCMD} ${COMICADDRESS} &
	fi
fi

# Remove in-progress flag
rm ${COMICNAME}going
