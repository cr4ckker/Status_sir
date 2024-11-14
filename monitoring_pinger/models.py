import os, subprocess, re

class Service:
    def __init__(self, name: str, cmd: str = 'service', control_results: list = [], logs_path: str = None):
        self.name = name
        self.cmd = cmd
        self.control_results = control_results
        self.logs_path = logs_path

    def get_logs(self):
        if self.logs_path and os.path.exists(self.logs_path):
            with open(self.logs_path) as f:
                return f.read()
        return "Logs file does not exist or was not set in the config"

    def check(self):
        if self.cmd == 'service':
            result = os.system(f'systemctl is-active --quiet {self.name}')
            if result:
                return False
            return True
        
        elif self.cmd == 'screen':
            output = subprocess.check_output(["screen -ls; true"], shell=True).decode()
            if f".{self.name}\t(" in output:
                return True
            return False
        
        elif self.cmd == 'tmux':
            output = subprocess.check_output(["tmux ls; true"], shell=True).decode()
            if f"{self.name}: " in output:
                return True
            return False

        else:
            output = subprocess.check_output([self.cmd], shell=True).decode()
            if output in self.control_results:
                return True
            return False