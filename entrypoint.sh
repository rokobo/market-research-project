#!/bin/sh

cd /ICB

python3.12 -m venv .venv
. .venv/bin/activate
pip3 install -r requirements.txt

exec gunicorn src.main:server -b 0.0.0.0:8060
