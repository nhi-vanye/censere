#! /bin/bash
#
# This is a local version of the CI script

function doit {

    echo ""
    echo "## $*"
    $*
    st=$?
    # this block the excution of subsequent tasks if this fails (returns a non-zero exit code)
    if [ "$st" -ne "0" ]
    then
        echo "Non-zero exit from $*"
        exit $st
    fi
}

if [ -z "${CENSERE_GITLAB_USER}" ]
then
    echo "You should set CENSERE_GITLAB_USER for a more consistant experience"
    exit 0
fi


echo "## build:censere"
echo "## ============="
doit scripts/lint.sh    -p ${CENSERE_GITLAB_USER} $*
doit scripts/test.sh    -p ${CENSERE_GITLAB_USER} $*
doit scripts/build.sh   -p ${CENSERE_GITLAB_USER} $*
doit scripts/tag.sh     -p ${CENSERE_GITLAB_USER} $*
doit scripts/push.sh    -p ${CENSERE_GITLAB_USER} $*
echo ""

