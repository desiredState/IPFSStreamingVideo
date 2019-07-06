#!/usr/bin/env bash

NAMESPACE=${NAMESPACE:='desiredstate'}
IMAGE=${IMAGE:='ipfsstreamingvideo'}
TAG=${VERSION:='latest'}
UPDATE=${UPDATE:=true}

if ! hash docker &>/dev/null; then
    echo 'Docker is required to run IPFSStreamingVideo. Please install it then try again.'
    exit 1
fi

if [[ "$UPDATE" = true ]] ; then
    docker pull "${NAMESPACE}/${IMAGE}:${TAG}"
fi

docker run -ti --rm "${NAMESPACE}/${IMAGE}:${TAG}" "${@}"
