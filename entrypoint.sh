#!/bin/sh

cd /ICB
echo "App"
ls -al
pip install --no-cache-dir -r requirements.txt

python src/main.py
