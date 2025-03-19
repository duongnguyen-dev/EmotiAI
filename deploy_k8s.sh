#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Create k8s cluster..."
cd infras/terraform
terraform init
terraform plan
terraform apply

echo "Create nginx-ingress namespace..."
kubectl create ns nginx-ingress
helm upgrade --install nginx-ingress-controller ./helm/nginx-ingress --namespace nginx-ingress

echo "Create main namespace and install required helm chart..."
kubectl create ns emotiai
helm upgrade --install airflow airflow-stable/airflow --namespace emotiai --values ./helm/airflow/values.yaml
helm upgrade --install mlflow oci://registry-1.docker.io/bitnamicharts/mlflow --namespace emotiai --values ./helm/mlflow/values.yaml
helm upgrade --install emotiai-source oci://registry-1.docker.io/bitnamicharts/postgresql --namespace emotiai --values helm/postgresql/values.yaml
helm upgrade --install emotiai-api ./helm/fastapi --namespace emotiai

echo "Create monitoring namespace and install required helm chart..."
kubectl create ns monitoring
helm upgrade --install prometheus --namespace monitoring oci://registry-1.docker.io/bitnamicharts/prometheus
helm upgrade --install grafana --values ./helm/grafana/values.yaml --namespace monitoring oci://registry-1.docker.io/bitnamicharts/grafana
helm upgrade --install jaeger  --values ./helm/jaeger/values.yaml --namespace monitoring oci://registry-1.docker.io/bitnamicharts/jaeger