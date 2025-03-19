#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Authenticate with Google Cloud
echo "Authenticating with Google Cloud..."
gcloud auth application-default login

# Define inventory and playbook paths
INVENTORY="inventory"
CREATE_INSTANCE_PLAYBOOK="deploy_jenkins/create_compute_instance.yaml"
DEPLOY_JENKINS_PLAYBOOK="deploy_jenkins/deploy_jenkins.yaml"

# Run Ansible playbook to create compute instance
echo "Creating compute instance..."
ansible-playbook -i "$INVENTORY" "$CREATE_INSTANCE_PLAYBOOK"

# Run Ansible playbook to deploy Jenkins
echo "Deploying Jenkins..."
ansible-playbook -i "$INVENTORY" "$DEPLOY_JENKINS_PLAYBOOK"

echo "Jenkins deployment completed successfully."