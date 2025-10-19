// Jenkins Pipeline for Chaos Engineering Tests
// Usage: Load this as a Jenkinsfile or include in your pipeline

pipeline {
    agent any
    
    environment {
        CHAOS_NAMESPACE = 'hello-world-app'
        CHAOS_TIMEOUT = '300'
        PYTHON_VERSION = '3.11'
    }
    
    stages {
        stage('Setup') {
            steps {
                script {
                    sh '''
                        python3 -m venv venv
                        source venv/bin/activate
                        pip install -r scripts/requirements.txt
                    '''
                }
            }
        }
        
        stage('Chaos Test: Pod Delete') {
            steps {
                script {
                    sh '''
                        source venv/bin/activate
                        python scripts/chaos-runner.py run pod-delete --namespace ${CHAOS_NAMESPACE}
                        sleep 30
                        python scripts/chaos-runner.py status pod-delete --namespace ${CHAOS_NAMESPACE}
                        python scripts/chaos-runner.py stop pod-delete --namespace ${CHAOS_NAMESPACE}
                    '''
                }
            }
        }
        
        stage('Chaos Test: CPU Stress') {
            steps {
                script {
                    sh '''
                        source venv/bin/activate
                        python scripts/chaos-runner.py run cpu-hog --namespace ${CHAOS_NAMESPACE}
                        sleep 30
                        python scripts/chaos-runner.py status cpu-hog --namespace ${CHAOS_NAMESPACE}
                        python scripts/chaos-runner.py stop cpu-hog --namespace ${CHAOS_NAMESPACE}
                    '''
                }
            }
        }
        
        stage('Chaos Test: Network Latency') {
            steps {
                script {
                    sh '''
                        source venv/bin/activate
                        python scripts/chaos-runner.py run network-latency --namespace ${CHAOS_NAMESPACE}
                        sleep 30
                        python scripts/chaos-runner.py status network-latency --namespace ${CHAOS_NAMESPACE}
                        python scripts/chaos-runner.py stop network-latency --namespace ${CHAOS_NAMESPACE}
                    '''
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        success {
            echo 'All chaos tests passed!'
        }
        failure {
            echo 'Chaos tests failed!'
        }
    }
}
