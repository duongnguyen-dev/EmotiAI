# EmotiAI
Emotion classification based on conversational data

# Overall architecture
<p align="center">
  <img src="https://github.com/duongnguyen-dev/EmotiAi/blob/main/assets/overall_architecture.png" />
</p>

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

# Installation and setup
# Development
- To run everything locally on Docker desktop for the first time, just run: `make up`.
- Without build: `make up-without-build`.
- Down everthing: `make down`.
- Access Airflow UI: 
- Access MLFlow UI:
- Access Minio UI:
- Access Prometheus UI:
- Access Grafana UI:
- Access Jaeger UI:

# Cloud deployment 
## Setup Jenkins CI/CD on GCE using Ansible 
- Run this command `make deploy_jenkins` to deploy Jenkins CI/CD on GKE.
## Setup others services on K8S using Terraform
1. Run this command `make deploy_k8s`
2. Go to minio service and create a bucket to store preprocessed data
```bash
kubectl exec -it "REPLACE WITH MINIO POD NAME"  -- /bin/bash
mc alias set myminio "MINIO URL" "MINIO ACCESS KEY" "MINIO SECRET KEY"
mc mb myminio/emotiai
```
3. Forward-port PostgresQL and run all scripts in folder `/data`