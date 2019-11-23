#! /bin/sh

topdir=$( cd "$( dirname "$0" )/../" && pwd )

NAME=mars-censere

# process the options

. ${topdir}/scripts/standard-args.sh
ParseArgs $*

if [ -n "${REGISTRY}" ]
then
    PULL=--pull
fi

set -x
docker build -t ${TAG} .
st=$?
docker image ls "${TAG}"
set +x
exit $st
