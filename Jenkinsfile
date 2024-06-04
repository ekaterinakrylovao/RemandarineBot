pipeline {
    agent any

    triggers {
        githubPush()
    }

    stages {
        stage('Check Docker-Compose') {
            steps {
                script {
                    def dockerComposePath = 'C:\\Program Files\\Docker\\Docker\\resources\\cli-plugins\\docker-compose.exe'
                    sh "set PATH=%PATH%;${dockerComposePath}"
                    sh "docker-compose --version"
                }
            }
        }
        stage('Build') {
            steps {
                echo 'Building...'
            }
        }
        stage('Download git repo') {
            steps {
                echo 'Downloading git repo...'
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
                echo 'Git repo downloaded'
            }
        }
        stage('Getting creds and env variables') {
            steps {
                echo 'Getting creds and env variables...'
                withCredentials([file(credentialsId: 'ENV', variable: 'ENV'), file(credentialsId: 'CREDS', variable: 'CREDS'), file(credentialsId: 'TOKEN', variable: 'TOKEN')]) {
                    script {
                        if (isUnix()) {
                            sh 'cp $ENV ./RemandarineBot/.env'
                            sh 'cp $CREDS ./RemandarineBot/credentials.json'
                            sh 'cp $TOKEN ./RemandarineBot/token.json'
                        } else {
                            bat 'powershell Copy-Item %ENV% -Destination ./RemandarineBot/.env'
                            bat 'powershell Copy-Item %CREDS% -Destination ./RemandarineBot/credentials.json'
                            bat 'powershell Copy-Item %TOKEN% -Destination ./RemandarineBot/token.json'
                        }
                    }
                }
                echo 'Creds and env variables retrieved'
            }
        }
    }
    post {
        success {
            echo 'Running docker...'
            script {
                if (isUnix()) {
                    sh 'cd RemandarineBot && docker-compose --version'
                    sh 'cd RemandarineBot && docker-compose up -d --build'
                } else {
                    bat 'cd RemandarineBot && C:\\Program Files\\Docker\\Docker\\resources\\cli-plugins\\docker-compose.exe --version'
                    bat 'cd RemandarineBot && C:\\Program Files\\Docker\\Docker\\resources\\cli-plugins\\docker-compose.exe up -d --build'
                }
            }
            echo 'Docker container is running successfully'
        }
    }
}