#!/bin/bash
pip install -r /app/requirements.txt -q
pytest tests/ -v --cov=app --cov-report=xml