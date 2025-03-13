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
        docker compose -f docker-compose.yaml up -d

        # Initialize Conda for the current shell session
        eval "$(conda shell.bash hook)"
        conda activate emotiai
        python data/create_table.py
        python data/insert_into_table.py
        python data/create_label_table.py
        python data/insert_label_data.py

        docker compose -f docker-compose.airflow.yaml up -d

        docker compose -f docker-compose.jenkins.yaml up -d

        docker compose -f docker-compose.api.yaml up -d 
        
        docker compose -f docker-compose.prom-graf.yaml up -d

        docker compose -f docker-compose.elk.yaml up -d

        ./keserve/build_kserve.sh
        ./kserve/run_kserve.sh
        ;;
    down)
        docker compose -f docker-compose.airflow.yaml down
        docker compose -f docker-compose.yaml down
        ;;
    up-without-build)
        docker compose -f docker-compose.elk.yaml up -d --no-build
        docker compose -f docker-compose.prom-graf.yaml up -d --no-build
        docker compose -f docker-compose.yaml up -d --no-build
        docker compose -f docker-compose.airflow.yaml up -d --no-build
        docker compose -f docker-compose.api.yaml up -d --no-build
        docker compose -f docker-compose.jenkins.yaml up -d --no-build
        ./kserve/run_kserve.sh
        ;;
    insert-data)
        # Initialize Conda for the current shell session
        eval "$(conda shell.bash hook)"
        conda activate emotiai
        python data/create_table.py
        python data/insert_into_table.py
        python data/create_label_table.py
        python data/insert_label_data.py
        ;;
    *)
        echo "Invalid command: $COMMAND"
        exit 1
        ;;
esac