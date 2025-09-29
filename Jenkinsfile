pipeline {
  agent any
  environment {
    DOCKERHUB_CREDENTIALS = 'dockerhub-creds'
    DOCKER_IMAGE = 'sathvikchandra77/tt-api'
    BUILD_TAG = "${env.BUILD_NUMBER}"
    RELEASE_TAG = "v${env.BUILD_NUMBER}"
  }
  stages {
      ...
