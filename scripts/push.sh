#! /bin/sh

topdir=$( cd "$( dirname "$0" )/../" && pwd )

NAME=mars-censere

. ${topdir}/scripts/standard-args.sh
ParseArgs $*

if [ -z "$REGISTRY" ]
then
    echo "push.sh: Ignoring request to push image, --registry not set"
    exit 0
fi

set -x
docker push ${REGISTRY}/${TAG}
st=$?
docker image ls "${REGISTRY}/${TAG}"
set +x
exit $st
