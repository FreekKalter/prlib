#!/bin/sh

tmux new-window 'source ./myenv/bin/activate; python run.py'
tmux new-window 'source ./myenv/bin/activate; celery -A prlib.celery worker -c 1'
cd ./prlib/frontend/
tmux split-window -v -t 2 'npm run build'
tmux split-window -h
cd ../
