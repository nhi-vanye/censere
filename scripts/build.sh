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

TAG=$(${date} +"${NAME}:%y.%m%d.%H%M")

set -x
set -euo pipefail
#docker pull ${NAME}:base || true
#docker pull ${NAME}:builder || true

docker buildx build --progress plain -o type=image -t ${TAG} .
st=$?
docker image ls "${NAME}"
#docker push ${NAME}:base
#docker push ${NAME}:builder
set +x
exit $st
