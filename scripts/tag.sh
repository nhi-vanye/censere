#! /bin/sh

topdir=$( cd "$( dirname "$0" )/../" && pwd )

NAME=censere

# process the options
. ${topdir}/scripts/standard-args.sh
ParseArgs $*

if [ -z "$REGISTRY" ]
then
    echo "tag.sh: Ignoring request to tag image, --registry not set"
    exit 0
fi

set -x
docker tag ${TAG} ${REGISTRY}/${TAG}
st=$?
set +x
exit $st
