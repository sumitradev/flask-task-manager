pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "flask-task-manager"
        DOCKER_TAG = "${BUILD_NUMBER}"
        SONAR_PROJECT_KEY = "flask-task-manager"
    }

    stages {

        // Stage 1 - Build
        stage('Build') {
            steps {
                echo 'Building Docker image...'
                sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"
            }
        }

        // Stage 2 - Test
        stage('Test') {
            steps {
                echo 'Running tests...'
                sh """
                    docker run --rm \
                    --volumes-from jenkins \
                    -w /var/jenkins_home/workspace/flask-task-manager \
                    python:3.11-slim \
                    bash /var/jenkins_home/workspace/flask-task-manager/run_tests.sh
                """
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: '**/test-results/*.xml'
                }
            }
        }

        // Stage 3 - Code Quality
        stage('Code Quality') {
            steps {
                echo 'Running SonarQube analysis...'
                sh """
                    docker run --rm \
                    --network jenkins \
                    --volumes-from jenkins \
                    -w /var/jenkins_home/workspace/flask-task-manager \
                    sonarsource/sonar-scanner-cli \
                    sonar-scanner
                """
            }
        }

        // Stage 4 - Security
        stage('Security') {
            steps {
                echo 'Running security scan...'
                sh """
                    docker run --rm \
                    -v \${WORKSPACE}:/src \
                    -w /src \
                    python:3.11-slim \
                    sh -c "pip install bandit -q && bandit -r app/ -f json -o bandit-report.json || true"
                """
                sh """
                    docker run --rm \
                    -v /var/run/docker.sock:/var/run/docker.sock \
                    aquasec/trivy:latest image \
                    --exit-code 0 \
                    --severity HIGH,CRITICAL \
                    ${DOCKER_IMAGE}:${DOCKER_TAG}
                """
            }
        }

        // Stage 5 - Deploy to Staging
        stage('Deploy') {
            steps {
                echo 'Deploying to staging...'
                sh "docker stop flask-task-manager-staging || true"
                sh "docker rm flask-task-manager-staging || true"
                sh """
                    docker run -d \
                    --name flask-task-manager-staging \
                    --network jenkins \
                    -p 5001:5000 \
                    ${DOCKER_IMAGE}:${DOCKER_TAG}
                """
                sh "sleep 5"
                sh "docker exec flask-task-manager-staging curl -f http://localhost:5000/health"
            }
        }

        // Stage 6 - Release to Production
        stage('Release') {
            steps {
                echo 'Releasing to production...'
                sh "docker stop flask-task-manager-production || true"
                sh "docker rm flask-task-manager-production || true"
                sh """
                    docker run -d \
                    --name flask-task-manager-production \
                    --network jenkins \
                    -p 5002:5000 \
                    ${DOCKER_IMAGE}:${DOCKER_TAG}
                """
                sh "sleep 5"
                sh "docker exec flask-task-manager-production curl -f http://localhost:5000/health"
                sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:release-${DOCKER_TAG}"
            }
        }

        // Stage 7 - Monitoring
        stage('Monitoring') {
            steps {
                echo 'Setting up monitoring...'
                sh "docker stop prometheus || true"
                sh "docker rm prometheus || true"
                sh """
                    docker run -d \
                    --name prometheus \
                    --network jenkins \
                    -p 9090:9090 \
                    -v \${WORKSPACE}/prometheus.yml:/etc/prometheus/prometheus.yml \
                    prom/prometheus:latest
                """
                sh "docker stop grafana || true"
                sh "docker rm grafana || true"
                sh """
                    docker run -d \
                    --name grafana \
                    --network jenkins \
                    -p 3000:3000 \
                    -e GF_SECURITY_ADMIN_PASSWORD=admin \
                    grafana/grafana:latest
                """
                echo 'Monitoring stack is up!'
                echo 'Prometheus: http://localhost:9090'
                echo 'Grafana: http://localhost:3000'
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
            echo "Application running at http://localhost:5002"
        }
        failure {
            echo 'Pipeline failed!'
        }
        always {
            echo 'Cleaning up...'
            sh "docker rmi ${DOCKER_IMAGE}:${DOCKER_TAG} || true"
        }
    }
}