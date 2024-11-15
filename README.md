# Status, sir!

Easy expandable service to monitor your server and service statuses. 
_powered with Python3.8+_

# Little introduction
_Disclaimer: I'm an amateur in making cross-platform installers and bash at all, so be careful with running install.sh_
_English is not my native language, so if you see typos, please let me know_

## Service structure: 

### Server + pinger _(monitoring_server/)_

Main side of a service.

**Server**: Provides the status page and functionality _(monitoring_server/server.py)_

**Pinger**: Checks the status of the servers every 10 seconds with **/healthcheck** request _(monitoring_server/pinger.py)_


### Receiver 

Node side that receives **/healthcheck** request by **Pinger**, gathers info, and returns it.

**Initial data:**
- IP and port of receiver's server
- Server's name
- List of service names

**Default healthcheck response has:**
- Status (Critical > Warning > Operational > Maintenance)
- CPU, RAM usage
- Service data:
  - Service name
  - Status (is it active)
- Extra data (Can be enriched with extensions)


# Installation and configuration

## Server

### 1. Clone the repository and open it:
```bash
git clone https://github.com/cr4ckker/Status_sir && cd Status_sir/monitoring_server
```
   
### 2. Install the dependencies:
- [Install Python3.8+](https://www.csestack.org/install-python-on-linux/)
- Install the packages 
```pip3 install -r reqs.txt```
- [Install tmux](https://github.com/tmux/tmux/wiki/Installing)
  
### 3. Edit the config and .env:
Create an environment file via .env.example
```bash
cp .env.example .env
```
Edit .env
```bash
nano .env
```
Edit config.py
```bash
nano config.py
```

### 4. _(Optional)_ Add autorun.sh in **crontab -e** to start the service on a server's startup:
_#TODO add this_
_Temporary solution. Will be changed soon_

### 5. Run
Run the server in new tmux session
```bash
tmux new -s status_sir python3 server.py
```
and pinger
```bash
tmux new -s pinger_sir python3 pinger.py
```

## Receiver

### 1. Clone the repository and open it:
```bash
git clone https://github.com/cr4ckker/Status_sir && cd Status_sir/monitoring_pinger
```

### 2. Install the dependencies
Installs tmux, python3, packages and adds autorun.sh in **crontab -l**
```bash
sudo ./install.sh
```

### 3. Edit the config and .env:

Create an environment file via .env.example
```bash
cp .env.example .env
```
Edit .env
```bash
nano .env
```
Edit config.py
```bash
nano config.py
```

### 4. Run
Run the server 
```bash
tmux new -s receiver python3 server.py
```
or just reboot the server ```reboot now``` and it will start automatically after.


# Little roadmap

1. Make installers easier
2. Provide network and ROM usage
3. Add Telegram authorization to control the rights of users (For example, see the status page, reboot the servers and etc.)

# Contributing

I'd love to see your PRs, if you want to help this project become better! 

_This README will rewritten later_
