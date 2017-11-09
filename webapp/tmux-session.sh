#!/bin/sh

ps ax| grep -v grep| grep "celery" -i | awk '{print $1}' | xargs kill
tmux new-window 'source ./myenv/bin/activate; python run.py'
tmux split-window -v -t 2 "source ./myenv/bin/activate;\
                           watchmedo auto-restart -d ./prlib -p '*tasks.py' -- \
                           celery -A prlib.celery worker -c 1 2>&1 | tee tasks.log"
cd ./prlib/frontend/
tmux split-window -h 'npm run build'
tmux select-pane -t 0
cd ../

