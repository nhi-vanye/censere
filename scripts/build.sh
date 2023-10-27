#! /bin/sh

topdir=$( cd "$( dirname "$0" )/../" && pwd )

NAME=mars-censere

date=date

if [ "$(uname -s)" == "Darwin" ]; then
    date=gdate
fi


TAG=$(${date} +"%y.%m%d.%H%M")



# process the options

. ${topdir}/scripts/standard-args.sh
ParseArgs $*

if [ -n "${REGISTRY}" ]
then
    PULL=--pull
fi

set -x
set -euo pipefail
docker pull ${NAME}:base || true
docker pull ${NAME}:builder || true

docker buildx build --progress plain -t ${TAG} .
st=$?
docker push ${NAME}:base
docker push ${NAME}:builder
docker image ls "${TAG}"
set +x
exit $st
