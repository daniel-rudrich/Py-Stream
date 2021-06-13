#!/bin/bash

# Start virtual environment
source venv/bin/activate

# Start Django server
cd src
python manage.py runserver