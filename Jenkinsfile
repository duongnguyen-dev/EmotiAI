pipeline {
    agent any // A node that execute the pipeline

    options{
        // Max number of build logs to keep and days to keep
        buildDiscarder(logRotator(numToKeepStr: '5', daysToKeepStr: '5'))
        // Enable timestamp at each job in the pipeline
        timestamps()
    }
    
    environment{
        registry = 'duongnguyen2911/emotiai-api'
        version = 'v2'
        registryCredential = 'dockerhub'      
    }

    stages {
        // stage('Test') {
        //     steps {
        //         script {
        //             echo 'Check dependencies...'
        //             sh 'pip install -r serving/requirements.txt'
        //         }
        //     }
        // }
        stage('Build') {
            steps {
                script {
                    echo 'Building image for deployment..'
                    sh 'ls'
                    dockerImage = docker.build("${registry}:${version}" , "--file dockerfile.api --platform linux/amd64 .")
                }
            }
        }
        stage('Push') {
            steps {
                script {
                    echo 'Pushing image to dockerhub..'
                    docker.withRegistry( '', registryCredential ) {
                        dockerImage.push()
                        dockerImage.push(version)
                    }
                }
            }
        }
        stage('Deploy') {
            agent {
                kubernetes {
                    containerTemplate {
                        name "helm"
                        image 'duongnguyen2911/emotiai-jenkins:v2'
                        alwaysPullImage true // Always pull image in case of using the same tag
                    }
                }
            }
            steps {
                echo 'Deploying models..'
                container('helm') {
                    sh("helm upgrade --install emotiai-api ./helm/fastapi --namespace emotiai")
                }
            }
        }
    }
}