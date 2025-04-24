#!/bin/sh
cd /app

pip install --no-cache-dir -r requirements.txt
ls -al
python src/main.py
