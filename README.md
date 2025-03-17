# EmotiAI
Emotion classification based on conversational data

# Overall architecture

# Prerequisite 
- Install these packages:
```bash
brew install buildpacks/tap/pack
brew install postgresql@17
brew install minio/stable/mc
brew install helm
```
- Create a new python environment using conda with python version >= 3.10:
```bash
conda create -n emotiai python=3.10
conda activate emotiai
```
- Install required dependencies:
```bash
pip install -r requirements.txt
pip install -r serving/requirements.txt
pip install -r kserve/requirements.txt
pip install -e .
```

# Development
- To run everything locally on Docker desktop for the first time, just run: `make up`.
- Without build: `make up-without-build`.
- Down everthing: `make down`.

# Deploy on k8s
- Run this command `make deploy` to deploy all the service on k8s via helm.

### Deploy jenkins on GCE using Ansible
- Add services account and generate key as json file, then put it into /secrets folder
- Run `gcloud auth application-default login`
- Then `ansible-playbook -i inventory deploy_jenkins/create_compute_instance.yaml`

### Installation and setup 
1. Go to minio service and create a bucket to store preprocessed data
```bash
kubectl exec -it "REPLACE WITH MINIO POD NAME"  -- /bin/bash
mc alias set myminio "MINIO URL" "MINIO ACCESS KEY" "MINIO SECRET KEY"
mc mb myminio/emotiai
```
4. Go to MLFlow tracking service and add the following:
```bash
echo Username: $(kubectl get secret --namespace emotiai mlflow-tracking -o jsonpath="{ .data.admin-user }" | base64 -d)
echo Password: $(kubectl get secret --namespace emotiai mlflow-tracking -o jsonpath="{.data.admin-password }" | base64 -d)

export MLFLOW_TRACKING_USERNAME="Username"
export MLFLOW_TRACKING_PASSWORD="Password"
```