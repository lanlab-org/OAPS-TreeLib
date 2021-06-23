pipeline {
    agent any

    stages {
        stage('MakeDatabasefile') {
	    steps {
	        sh 'touch ./database.db && rm -f ./database.db' 
	        sh 'cat ./database.sql | sqlite3 ./database.db'
	    }
	}
        stage('BuildIt') {
            steps {
                echo 'Building..'
		sh 'sudo docker build -t OAPS-TreeLib .'
		sh 'sudo docker stop $(docker ps -aq)'
		sh 'sudo docker run -d -p 91:80 -v /var/lib/jenkins/workspace/EnglishPal_Pipeline_master/frequency:/frequency -t OAPS-TreeLib'
            }
        }
        stage('TestIt') {
            steps {
                echo 'Testing..'
		sh 'sudo docker run -d -p 4444:4444 selenium/standalone-chrome'
		sh 'pip3 install pytest -U -q'
		sh 'pip3 install selenium -U -q'
		sh 'pytest -v -s --html=TreeLibTestReport.html .'
            }
        }
        stage('DeployIt') {
            steps {
                echo 'Deploying (TBD)'
            }
        }
    }
}
