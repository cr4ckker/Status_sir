from models import Service

server_name = 'Server Name #N'

services = [
    Service('first_service', 'tmux'), # Service example started on tmux
    Service('second_service', 'screen'), # Service example started on screen
    Service('third_service'), # Service example that you can see in systemctl
    Service('forth_service', 'some_cmd | grep ... | cut ...', ['forth_service: ']) # Service example with custom check and control check word (if cmd output is in check words then it's appears to be Operational)
]