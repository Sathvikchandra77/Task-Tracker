pipeline {
  agent any
  environment {
    // ID of the Docker Hub credentials you created in Jenkins
    DOCKERHUB_CREDENTIALS = 'dockerhub-creds'
    // Your Docker Hub repository
    DOCKER_IMAGE = 'sathvikchandra77/tt-api'
    BUILD_TAG = "${env.BUILD_NUMBER}"
    RELEASE_TAG = "v${env.BUILD_NUMBER}"
  }

  stages {

    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build') {
      steps {
        sh 'python -m pip install --upgrade pip'
        sh 'pip install -r requirements.txt'
        sh "docker build -t ${DOCKER_IMAGE}:${BUILD_TAG} ."
      }
    }

    stage('Test') {
      steps {
        sh 'python -m pytest -q --junitxml=report.xml'
      }
      post {
        always {
          junit 'report.xml'
        }
      }
    }

    stage('Security') {
      steps {
        sh 'pip install bandit pip-audit'
        sh 'bandit -r app -f txt -o bandit.txt || true'
        sh 'pip-audit -r requirements.txt -f json -o pip_audit.json || true'
      }
      post {
        always {
          archiveArtifacts artifacts: 'bandit.txt,pip_audit.json', fingerprint: true
        }
      }
    }

    stage('Deploy (Staging)') {
      steps {
        sh "BUILD_TAG=${BUILD_TAG} docker compose -f docker-compose.staging.yml up -d --build"
        sh "sleep 3 && curl -fsS http://localhost:8081/health"
      }
    }

    stage('Release (Prod)') {
      when { branch 'main' }
      steps {
        input message: 'Promote to production?', ok: 'Release'
        withCredentials([usernamePassword(credentialsId: "${DOCKERHUB_CREDENTIALS}", usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
          sh 'echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin'
        }
        sh "docker tag ${DOCKER_IMAGE}:${BUILD_TAG} ${DOCKER_IMAGE}:${RELEASE_TAG}"
        sh "docker push ${DOCKER_IMAGE}:${RELEASE_TAG}"
        sh "RELEASE_TAG=${RELEASE_TAG} docker compose -f docker-compose.prod.yml up -d"
        sh "sleep 5 && curl -fsS http://localhost:8080/health"
      }
    }

    stage('Monitoring & Evidence') {
      steps {
        sh 'curl -fsS http://localhost:8080/health > health_status.json || echo "{}" > health_status.json'
        archiveArtifacts artifacts: 'health_status.json', fingerprint: true
      }
    }
  }

  post {
    always {
      echo "Pipeline finished with status: ${currentBuild.currentResult}"
    }
  }
}
