#! /bin/sh

topdir=$( cd "$( dirname "$0" )/../" && pwd )

NAME=censere

# process the options

. ${topdir}/scripts/standard-args.sh
ParseArgs $*

pylint censere
st=$?
set +x
exit $st
