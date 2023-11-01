#! /bin/sh

topdir=$( cd "$( dirname "$0" )/../" && pwd )

NAME=mars-censere

# process the options
. ${topdir}/scripts/standard-args.sh
ParseArgs $*

set -x
set -euo pipefail

python -m build
st=$?
ls -l dist
set +x
exit $st
