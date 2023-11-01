#! /bin/sh

topdir=$( cd "$( dirname "$0" )/../" && pwd )

NAME=mars-censere

date=date

if [ "$(uname -s)" == "Darwin" ]; then
    date=gdate
fi

# process the options

. ${topdir}/scripts/standard-args.sh
ParseArgs $*

if [ -n "${REGISTRY}" ]
then
    PULL=--pull
fi

set -x
set -euo pipefail

echo docker buildx build --progress plain -o type=image -t ${NAME}:${TAG} .
exit 0
st=$?
docker image ls "${NAME}"
set +x
exit $st
