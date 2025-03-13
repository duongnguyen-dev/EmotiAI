1. Get the MLflow URL by running these commands:

  NOTE: It may take a few minutes for the LoadBalancer IP to be available.
        Watch the status with: 'kubectl get svc --namespace emotiai -w mlflow-tracking'

   export SERVICE_IP=$(kubectl get svc --namespace emotiai mlflow-tracking --template "{{ range (index .status.loadBalancer.ingress 0) }}{{ . }}{{ end }}")
   echo "MLflow URL: http://$SERVICE_IP/"

2. Open a browser and access MLflow using the obtained URL.
3. Login with the following credentials below to see your blog:

  echo Username: $(kubectl get secret --namespace emotiai mlflow-tracking -o jsonpath="{ .data.admin-user }" | base64 -d)
  echo Password: $(kubectl get secret --namespace emotiai mlflow-tracking -o jsonpath="{.data.admin-password }" | base64 -d)

Accessing minio console please try
kubectl port-forward --namespace emotiai $(kubectl get pod --namespace emotiai --selector="app.kubernetes.io/instance=mlflow,app.kubernetes.io/name=minio" --output jsonpath='{.items[0].metadata.name}') 8080:minio-console
echo Username: $(kubectl get secret --namespace emotiai mlflow-minio -o jsonpath="{ .data.root-user }" | base64 -d)
echo Password: $(kubectl get secret --namespace emotiai mlflow-minio -o jsonpath="{ .data.root-password }" | base64 -d)


echo Password: $(kubectl get secret --namespace emotiai mlflow-postgresql -o jsonpath="{ .data.user-password }" | base64 -d)