#! /bin/sh

topdir=$( cd "$( dirname "$0" )/../" && pwd )

NAME=mars-censere

# process the options

. ${topdir}/scripts/standard-args.sh
ParseArgs $*

pytest -v tests
st=$?
set +x
exit $st
