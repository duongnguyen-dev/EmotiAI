helm upgrade --install airflow airflow-stable/airflow --namespace emotiai --values ./helm/airflow/values.yaml
helm upgrade --install mlflow oci://registry-1.docker.io/bitnamicharts/mlflow --namespace emotiai --values ./helm/mlflow/values.yaml
helm upgrade --install emotiai-source oci://registry-1.docker.io/bitnamicharts/postgresql --namespace emotiai --values helm/postgresql/values.yaml

kubectl port-forward --namespace emotiai svc/emotiai-source-postgresql 5439:5432 & PGPASSWORD=emotiai psql --host 127.0.0.1 -U emotiai -d goemotion -p 5432

kubectl port-forward --namespace emotiai $(kubectl get pod --namespace emotiai --selector="app.kubernetes.io/instance=mlflow,app.kubernetes.io/name=minio" --output jsonpath='{.items[0].metadata.name}') 8080:minio-console
echo Username: $(kubectl get secret --namespace emotiai mlflow-minio -o jsonpath="{ .data.root-user }" | base64 -d)
echo Password: $(kubectl get secret --namespace emotiai mlflow-minio -o jsonpath="{ .data.root-password }" | base64 -d)