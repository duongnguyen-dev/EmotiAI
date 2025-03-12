#!/bin/bash
SCRIPT_DIR="$( cd -- $( dirname -- ${BASH_SOURCE[0]}s ) &> /dev/null && pwd )"
PARENT_DIR="$( dirname "$SCRIPT_DIR" )"

pack build \
    --builder=heroku/builder:24 \
    --platform linux/arm64 \
    --volume $PARENT_DIR/src:/workspace/src \
    duongnguyen2911/emotiai-kserve:v1
docker push duongnguyen2911/emotiai-kserve:v1