#!/bin/sh

cd /
echo "/"
ls -al

cd /app
echo "App"
ls -al
pip install --no-cache-dir -r requirements.txt

python src/main.py
