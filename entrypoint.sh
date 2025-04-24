#!/bin/bash

cd /ICB

python3.12 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt

gunicorn src.main:server --daemon -b 127.0.0.1:8060
