#!/bin/bash

# Start virtual environment
source venv/bin/activate

# Start Django server
cd src
if [$1 -eq "network" ]
    then
        python manage.py runserver 0.0.0.0:8000
else
    python manage.py runserver
fi
