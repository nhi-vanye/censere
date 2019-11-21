#! /bin/sh

imagedir=$( cd "$( dirname "$0" )/../" && pwd )

NAME=$(basename ${imagedir} )

# process the options


ParseArgs()
{
    usage() {
        cat <<EOF

Usage: $1 -d <arg> [ -p <args> -r <arg> -f <arg> -k ]

Options:

    -d DIRECTORY    - build DIRECTORY (required)
    -p PROJEECT     - used in CI builds - should be set from CI_PROJECT_NAMESPACE
    -r REGISTRY     - if set then push images to REGISTRY - must be logged in already.
    -t TAG          - if set then used as name of image
    -f DOCKERFILE   - if set then pre-process the file DIRECTORY/Dockerfile and
                      write to DOCKERFILE - used to update FROM line in Dockerfiles
                      to allow builds across branches and repositories.
    -i DOCKERFILE   - use this DOCKERFILE as source during prep step
    -k              - keep temporary files (i.e. DOCKERFILE ) .

Note all options are applicable to all scripts, but the same options are
allowed (and ignored) for all scripts

EOF
        exit
    }

    OPTIND=1

    while getopts "d:p:r:f:kmi:t:" arg; do
        case "${arg}" in
            d)
                DIR=${OPTARG}
                ;;
            p)
                PROJECT=${OPTARG}
                ;;
            r)
                REGISTRY=${OPTARG}
                ;;
            i)
                DOCKERFILEIN=${OPTARG}
                ;;
            f)
                DOCKERFILE=${OPTARG}
                ;;
            t)
                TAG=${OPTARG}
                ;;
            k)
                CLEAN=false
                ;;
            m)
                MASTER=true
                ;;
            *)
                usage $0
                ;;
        esac
    done

    shift $((OPTIND-1))

    if [ -n "${PROJECT}" ]
    then
        TAG=${PROJECT}/censere:latest
    else
        TAG=${DIR}censere:latest
    fi

}

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
