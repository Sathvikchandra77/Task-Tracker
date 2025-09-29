pipeline {
  agent any
  environment {
    // Jenkins credentials ID for your Docker Hub login
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
        bat 'python -m pip install --upgrade pip'
        bat 'pip install -r requirements.txt'
        bat "docker build -t %DOCKER_IMAGE%:%BUILD_TAG% ."
      }
    }

    stage('Test') {
      steps {
        bat 'python -m pytest -q --junitxml=report.xml'
      }
      post {
        always {
          junit 'report.xml'
        }
      }
    }

    stage('Security') {
      steps {
        bat 'pip install bandit pip-audit'
        // run Bandit and pip-audit; allow build to continue even if issues are found
        bat 'bandit -r app -f txt -o bandit.txt || exit 0'
        bat 'pip-audit -r requirements.txt -f json -o pip_audit.json || exit 0'
      }
      post {
        always {
          archiveArtifacts artifacts: 'bandit.txt,pip_audit.json', fingerprint: true
        }
      }
    }

    stage('Deploy (Staging)') {
      steps {
        // timeout 3 seconds and then check health endpoint
        bat "docker compose -f docker-compose.staging.yml up -d --build"
        bat "timeout /t 3 >nul"
        bat "powershell -Command \"Invoke-WebRequest http://localhost:8081/health -UseBasicParsing\""
      }
    }

    stage('Release (Prod)') {
      when { branch 'main' }
      steps {
        input message: 'Promote to production?', ok: 'Release'
        withCredentials([usernamePassword(credentialsId: "${DOCKERHUB_CREDENTIALS}", usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
          bat 'echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin'
        }
        bat "docker tag %DOCKER_IMAGE%:%BUILD_TAG% %DOCKER_IMAGE%:%RELEASE_TAG%"
        bat "docker push %DOCKER_IMAGE%:%RELEASE_TAG%"
        bat "docker compose -f docker-compose.prod.yml up -d"
        bat "timeout /t 5 >nul"
        bat "powershell -Command \"Invoke-WebRequest http://localhost:8080/health -UseBasicParsing\""
      }
    }

    stage('Monitoring & Evidence') {
      steps {
        bat "powershell -Command \"Invoke-WebRequest http://localhost:8080/health -UseBasicParsing | Out-File -Encoding utf8 health_status.json\""
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
