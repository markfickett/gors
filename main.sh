#!/bin/bash
# Main file for comics
# Check for comic updates (and open updated comics' pages);
#	optional arguments specify which comics to check
# Mark Fickett [ naib.webhop.org ], 2008 March 08

# For ease of access, this goes in ~/.profile :
# alias comics='OLDDIR=`pwd` && cd ~/comics/ && ./main.sh && cd $OLDDIR'

# Where is this file (and comics.sh) located?
# Used in case of invocation from non-local directory or double-clicking
BASE=`echo $0 | sed -e 's/[^\/]*$//g'`
cd ${BASE}

# Check for required files
RUN=./comics.sh
if test ! -f $RUN
then
	echo "Unable to find $RUN in ${BASE}"
	exit 1
fi

# Run $RUN for all comics in the $CONF file, reading argument lists as
# whitespace-separated tokens until a '&'.
# If arguments are provided, run only the listed comics.

CONF=comics.conf
ARGLIST=''
CNAME=''
SKIP="NO"
PREV=''
for token in `cat $CONF`
do
	if [ \( "$PREV" = "--name" \) -o \( "$PREV" = "-n" \) ]
	then
		CNAME=$token
	fi
	if [ $token = '#' ]
	then
		SKIP="YES"
	fi
	if [ $token = '&' ]
	then
		if [ $# -gt 0 ]
		then
			SKIP="YES"
			for comicname in $*
			do
				if [ "$CNAME" = "$comicname" ]
				then
					SKIP="NO"
				fi
			done
		fi
		if [ $SKIP = "NO" ]
		then
			# echo running for $CNAME
			# echo running: $RUN $ARGLIST
			$RUN $ARGLIST &
		fi
		ARGLIST=''
		CNAME=''
		SKIP="NO"
	else
		ARGLIST="$ARGLIST $token"
	fi
	# echo WIP: $ARGLIST
	PREV=$token
done

# Wait for things to finish up - we want fast parallel execution,
# but we don't want to mess up the CL

GOINGFILES='nonegoing'
HADONE='no'
EVERY=80
COUNTER=0
until [ $GOINGFILES = '*going' ]
do
	sleep .25
	GOINGFILES=*going
	GOINGFILES=`echo $GOINGFILES | tr -d ' '`
	if [ $GOINGFILES = '*going' ]
	then
		if [ $HADONE = 'no' ]
		then
			GOINGFILES='nonegoing'
			echo protecting...
		fi
	else
		HADONE='yes'
		let COUNTER=$COUNTER+1
		if [ $COUNTER -ge $EVERY ]
		then
			COUNTER=0
			echo "Waiting on: " $GOINGFILES
		fi
	fi
done

