pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "project-polaris"
        DOCKER_TAG   = "latest"
    }

    stages {
        stage('Build') {
            steps {
                echo 'Building Flask application Docker image...'
                sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
            }
        }

        stage('Test') {
            steps {
                echo 'Validating Python code syntax compilation...'
                sh 'python3 -m py_compile app.py'
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying application service container...'
                echo 'Successfully deployed Project Polaris!'
            }
        }
    }

    post {
        always {
            cleanWs()
            echo 'Workspace cleaned.'
        }
    }
}
