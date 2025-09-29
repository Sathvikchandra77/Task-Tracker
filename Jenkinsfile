pipeline {
  agent any
  environment {
    DOCKERHUB_CREDENTIALS = 'dockerhub-creds'     // Jenkins creds ID
    DOCKER_IMAGE = 'sathvikchandra77/tt-api'      // your Docker Hub repo
    BUILD_TAG    = "${env.BUILD_NUMBER}"
    RELEASE_TAG  = "v${env.BUILD_NUMBER}"
  }

  stages {

    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Build Image') {
      steps {
        // Build the app image (it already installs requirements.txt)
        bat "docker build -t %DOCKER_IMAGE%:%BUILD_TAG% ."
      }
    }

    stage('Test (inside Docker)') {
      steps {
        // Run pytest INSIDE the container with workspace mounted at /work
        // Write JUnit report to the host workspace.
        bat """
          docker run --rm ^
            -e PYTHONPATH=/work ^
            -v %CD%:/work ^
            -w /work ^
            %DOCKER_IMAGE%:%BUILD_TAG% ^
            python -m pytest -q --junitxml=report.xml
        """
      }
      post {
        always { junit 'report.xml' }
      }
    }

    stage('Security (inside Docker)') {
      steps {
        // bandit: write findings to bandit.txt in workspace
        bat """
          docker run --rm ^
            -v %CD%:/work ^
            -w /work ^
            %DOCKER_IMAGE%:%BUILD_TAG% ^
            bandit -r app -f txt -o bandit.txt || exit 0
        """
        // pip-audit: audit requirements.txt; write JSON to workspace
        bat """
          docker run --rm ^
            -v %CD%:/work ^
            -w /work ^
            %DOCKER_IMAGE%:%BUILD_TAG% ^
            pip-audit -r requirements.txt -f json -o pip_audit.json || exit 0
        """
      }
      post {
        always { archiveArtifacts artifacts: 'bandit.txt,pip_audit.json', fingerprint: true }
      }
    }

    stage('Deploy (Staging)') {
      steps {
        // Bring up staging (maps 8081->8000); verify /health
        bat "docker compose -f docker-compose.staging.yml up -d --build"
        bat "timeout /t 3 >nul"
        bat "powershell -Command \"Invoke-WebRequest http://localhost:8081/health -UseBasicParsing | Out-Null\""
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
        bat "powershell -Command \"Invoke-WebRequest http://localhost:8080/health -UseBasicParsing | Out-Null\""
      }
    }

    stage('Monitoring & Evidence') {
      steps {
        // Save a copy of prod health response as build artifact
        bat "powershell -Command \"Invoke-WebRequest http://localhost:8080/health -UseBasicParsing | Out-File -Encoding utf8 health_status.json\""
        archiveArtifacts artifacts: 'health_status.json', fingerprint: true
      }
    }
  }

  post {
    always { echo "Pipeline finished with status: ${currentBuild.currentResult}" }
  }
}
