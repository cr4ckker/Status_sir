#!/bin/bash -il

# To install:
#   - chmod a+x ~/autorun.sh
#   - run "crontab -e" and add this line:
#     @reboot /bin/bash -li ~/autorun.sh

start_tmux_session() {
    if tmux has-session -t $1 > /dev/null 2>&1; then
        :
    else
        tmux new-session -d -s $1 "cd $2 && $3"
    fi
}

# Defining services to start on a server startup

start_tmux_session status "~/status" "python3 server.py"