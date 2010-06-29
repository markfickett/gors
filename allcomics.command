#!/bin/sh

#####
# This file is deprecated in favor of main.sh, in combination with comics.conf
# As of 2008 March 09
#####

# Check all the comics
# For lack of better generalization, run a bunch of times with diff. arguments

# Mark Fickett [ naib.webhop.org ]
# Last updated 2006 May 19

# Where is this file (and comics.sh) located?
# Used in case of invocation from non-local directory or double-clicking
BASE=`echo $0 | sed -e 's/[^\/]*$//g'`
# OLDPWD=`pwd`
cd ${BASE}

if test ! -f comics.sh
then
	echo "Unable to find comics.sh in ${BASE}"
	cd ${OLDPWD}
	exit
fi

# For ease of access, this goes in ~/.profile :
# alias comics='OLDDIR=`pwd` && cd ~/comics/ && ./allcomics.sh && cd $OLDDIR'

./comics.sh qwantz http://qwantz.com \
	'http:\/\/www\.qwantz\.com\/comics\/comic.*\.png' &
./comics.sh qc http://questionablecontent.net/ \
	'http:\/\/www\.questionablecontent\.net\/comics\/.*\.png' &
./comics.sh bunny http://www.bunny-comic.com/ \
	'strips\/.*\..*' &
./comics.sh gc http://www.gunnerkrigg.com/index2.php \
	'http:\/\/www\.gunnerkrigg\.com.*comics\/.*\..*' &
./comics.sh scarygoround http://www.scarygoround.com/ \
	'strips.*' &
./comics.sh catandgirl http://catandgirl.com/ \
	'http:\/\/catandgirl.com\/archive\/.*\.gif' &
#	'http:\/\/static.flickr.com\/.*\/.*\..*' &
./comics.sh shortpacked http://www.shortpacked.com/ \
	'\/comics\/.*\..*' &
./comics.sh ddoi http://wvs.topleftpixel.com/ \
	'http:\/\/wvs.topleftpixel.com\/photos\/.*\..*' &
./comics.sh postsecret http://postsecret.blogspot.com/ \
	'http:\/\/bp.\.blogger\.com\/.*\.jpg' &
./comics.sh drmcninja http://drmcninja.com/ \
	'http:\/\/drmcninja\.com\/page\.php..*' a href 2 &
./comics.sh samandfuzzy http://www.samandfuzzy.com/index.php \
	'comics\/.*\..*' &
./comics.sh webkit http://webkit.org/blog/ \
	'post-.*' div id &
./comics.sh xkcd http://www.xkcd.com/ \
	'http:\/\/imgs\.xkcd\.com\/comics\/.*' &
./comics.sh asofterworld http://www.asofterworld.com/ \
	'http:\/\/www.asofterworld.com\/clean\/.*\.jpg' &
./comics.sh girlgenius http://www.girlgeniusonline.com/comic.php \
	'http:\/\/www\.girlgeniusonline.com\/ggmain\/strips\/.*\.jpg' IMG SRC &
./comics.sh visualnotebook http://www.a-visual-notebook.at/index.php \
	'images\/200.*\.jpg' &
./comics.sh lowresolution http://lowresolution.com/ \
	'http:\/\/www\.lowresolution\.com\/images\/.*\.jpg' &
./comics.sh dicebox http://www.dicebox.net/thelatest.htm \
	'chap.\/images\/.*.jpg' &
./comics.sh 3ps http://www.threepanelsoul.com/index.php \
	'http:\/\/www\.threepanelsoul\.com\/comics\/.*\..*' &
./comics.sh abominable http://horhaus.com/abominable/ \
	'http:\/\/horhaus.com\/abominable\/comics\/.*\.jpg' &
./comics.sh talesofmu http://www.talesofmu.com/story/ \
	'http:\/\/.*talesofmu.*\.com\/story\/book.*\/.*...' a href &

# ./comics.sh cad http://ctrlaltdel-online.com/comic.php \
#	'\/comics\/.*\.jpg' &
# ./comics.sh dooce http://dooce.com/ \
#	'.*' h1 id &
# ./comics.sh orneryboy http://www.orneryboy.com/index.php \
#	'http:\/\/www.orneryboy.com\/index.php.comicID=.*' a href 2 &
# ./comics.sh flakypastry http://flakypastry.runningwithpencils.com/ \
#	'comics\/.*-.*\..*\.jpg' &
# ./comics.sh wondermark http://www.wondermark.com/index.html \
#	'\/comics\/.*\..*' &
# ./comics.sh afterstrife http://www.afterstrife.com/index.php \
#	'strips\/....-..-..\.gif' &

# Wait for things to finish up - we want fast parallel execution,
# but we don't want to mess up the CL
# Assume we don't get here before anything has touched *going

GOINGFILES='nonegoing'
HADONE='no'
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
	fi
done

# cd ${OLDPWD}
