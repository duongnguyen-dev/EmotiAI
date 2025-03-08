#!/bin/bash

# Ensure a command is provided
if [ -z "$1" ]; then
    echo "Usage: $0 {up|down|up-without-build}"
    exit 1
fi

COMMAND=$1

# Execute the Docker Compose command
case "$COMMAND" in
    up)
        docker compose -f docker-compose.yaml up build
        docker compose -f docker-compose.yaml up -d --no-build

        # Initialize Conda for the current shell session
        eval "$(conda shell.bash hook)"
        conda activate emotiai
        python data/create_table.py
        python data/insert_into_table.py
        python data/create_label_table.py
        python data/insert_label_data.py

        docker compose -f docker-compose.airflow.yaml build
        docker compose -f docker-compose.airflow.yaml up -d --no-build

        docker compose -f docker-compose.jenkins.yaml build
        docker compose -f docker-compose.jenkins.yaml up -d --no-build
        ;;
    down)
        docker compose -f docker-compose.airflow.yaml down
        docker compose -f docker-compose.yaml down
        ;;
    up-without-build)
        docker compose -f docker-compose.yaml up -d --no-build
        docker compose -f docker-compose.airflow.yaml up -d --no-build
        docker compose -f docker-compose.jenkins.yaml up -d --no-build
        ;;
    *)
        echo "Invalid command: $COMMAND"
        exit 1
        ;;
esac