pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo 'Building...'
            }
        }
        stage('Download git repo') {
            steps {
                echo '===============downloading git repo==================='
                script {
                    if (isUnix()) {
                        sh 'rm -rf RemandarineBot'
                        sh 'git clone --depth=1 https://github.com/ekaterinakrylovao/RemandarineBot.git'
                        sh 'rm -rf RemandarineBot/.git*'
                    } else {
                        bat 'powershell -Command "Get-ChildItem -Path .\\* -Recurse | Remove-Item -Force -Recurse"'
                        bat 'git clone --depth=1 https://github.com/ekaterinakrylovao/RemandarineBot.git'
                        bat 'powershell Remove-Item RemandarineBot/.git* -Recurse -Force'
                    }
                }
                echo '===============git repo downloaded==================='
            }
        }
        stage('Getting creds and env variables') {
            steps {
                echo '===============getting env variables==================='
                withCredentials([file(credentialsId: 'ENV', variable: 'ENV'), file(credentialsId: 'CREDS', variable: 'CREDS'), file(credentialsId: 'TOKEN', variable: 'TOKEN')]) {
                    script {
                        if (isUnix()) {
                            sh 'cp $ENV ./RemandarineBot/.env'
                            sh 'cp $REDS ./RemandarineBot/credentials.json'
                            sh 'cp $TOKEN ./RemandarineBot/token.json'
                        } else {
                            bat 'powershell Copy-Item %ENV% -Destination ./RemandarineBot/.env'
                            bat 'powershell Copy-Item %CREDS% -Destination ./RemandarineBot/credentials.json'
                            bat 'powershell Copy-Item %TOKEN% -Destination ./RemandarineBot/token.json'
                        }
                    }
                }
                echo '===============got creds and env variables==================='
            }
        }
    }
    post {
        success {
            echo '===============run docker==================='
                script {
                    if (isUnix()) {
                        sh 'cd RemandarineBot && docker-compose up -d --build'
                    } else {
                        bat 'cd RemandarineBot && docker-compose up -d --build'
                    }
                }
                echo '===============docker container is running successfully==================='
            }
        }
    }