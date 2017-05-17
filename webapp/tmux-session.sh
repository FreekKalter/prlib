#!/bin/sh

tmux new-window 'source ./myenv/bin/activate; python run.py'
tmux split-window -v -t 2 'source ./myenv/bin/activate; celery -A prlib.celery worker -c 1'
cd ./prlib/frontend/
tmux split-window -h 'npm run build'
tmux select-pane -t 0
cd ../

