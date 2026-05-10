#!/bin/bash
cd /var/jenkins_home/workspace/flask-task-manager
pip install -r requirements.txt -q
pytest tests/ -v --cov=app --cov-report=xml