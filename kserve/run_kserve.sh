#!/bin/bash
SCRIPT_DIR="$( cd -- $( dirname -- ${BASH_SOURCE[0]}s ) &> /dev/null && pwd )"
PARENT_DIR="$( dirname "$SCRIPT_DIR" )"

# Source the .env file to load environment variables
if [ -f "$PARENT_DIR/.env" ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo ".env file not found!"
    exit 1
fi

docker run \
    --name emoti-kserve-api \
    -ePORT=8080 \
    -p8080:8080 \
    --network emotiai_default \
    --env MINIO_ENDPOINT_URL=$MINIO_ENDPOINT_URL \
    --env MLFLOW_TRACKING_URI=$MLFLOW_TRACKING_URI \
    --env MLFLOW_REGISTERED_MODEL=$MLFLOW_REGISTERED_MODEL \
    --env MLFLOW_ARTIFACTS_DESTINATION=$MLFLOW_ARTIFACTS_DESTINATION \
    --env MINIO_ACCESS_KEY=$MINIO_ACCESS_KEY \
    --env MINIO_SECRET_KEY=$MINIO_SECRET_KEY \
    duongnguyen2911/emotiai-kserve:v1