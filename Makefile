.PHONY: up down up-without-build

up: 
	bash ./run.sh up
down: 
	bash ./run.sh down
up-without-build:
	bash ./run.sh up-without-build
deploy_k8s:
	bash ./deploy_k8s.sh
deploy_jenkins:
	bash ./deploy_jenkins.sh