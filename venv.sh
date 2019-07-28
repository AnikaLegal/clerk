#!/bin/bash
# Setup local virtual env for editor
if [ ! -d env ]
then
    # Create virutal environment, install python packages.
    virtualenv -p python3 env
    . env/bin/activate
    pip3 install -r app/requirements.txt
else
    . env/bin/activate
fi
