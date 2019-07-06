#!/usr/bin/env bash

set -e

function usage {
    cat <<EOF
usage: factory [-h] {build,test,push,all} ...

positional arguments:
  {build,test,push,all}
    build               build the Docker Image
    push                push the Docker Image

optional arguments:
  -h, --help            display this help message
EOF
}

function check_deps {
    # Dependencies which should be in PATH.
    DEPS=( 'docker' )

    for i in "${DEPS[@]}"; do
        if ! hash "${i}" 2>/dev/null; then
            echo -e "${RED}BUILD > "${i}" is required. Please install it then try again.${NONE}"
            exit 1
        fi
    done
}

function build {
    # Build Docker Image.
    echo -e "${MAGENTA}BUILD > Building the ${NAMESPACE}/${IMAGE}:${TAG} Docker Image...${NONE}"
    docker build -t "${NAMESPACE}/${IMAGE}:${TAG}" .
    echo -e "${GREEN}BUILD > OK.${NONE}"
}

function push {
    # Push Docker Image.
    echo -e "${MAGENTA}BUILD > Pushing the ${NAMESPACE}/${IMAGE}:${TAG} Docker Image...${NONE}"
    docker push "${NAMESPACE}/${IMAGE}:${TAG}"
    echo -e "${GREEN}BUILD > OK.${NONE}"
}

# Environment variable overrides.
export NAMESPACE=${NAMESPACE:='desiredstate'}
export IMAGE=${IMAGE:='ipfsstreamingvideo'}
export TAG=${VERSION:='latest'}
export UPDATE=${UPDATE:=false} # false as we're building the Image locally.

MAGENTA=$(tput setaf 5)
GREEN=$(tput setaf 2)
RED=$(tput setaf 1)
NONE=$(tput sgr 0)

check_deps

case $1 in
    build)
        build
        ;;
    push)
        push
        ;;
    *)
        usage
        exit 1
esac

echo -e "${GREEN}BUILD > Finished.${NONE}"
