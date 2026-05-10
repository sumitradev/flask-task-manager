#!/bin/bash
cd /var/jenkins_home/workspace/flask-task-manager
pip install -r requirements.txt -q
pip install pytest-junit -q
pytest tests/ -v --cov=app --cov-report=xml --junit-xml=test-results/results.xml
mkdir -p test-results