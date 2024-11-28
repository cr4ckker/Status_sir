#!/bin/bash

original_dir=$(pwd)

install_python_debian() {
  echo "Установка Python 3.10 на систему Debian/Ubuntu..."
  sudo apt update
  sudo apt install -y software-properties-common
  sudo add-apt-repository ppa:deadsnakes/ppa
  sudo apt update
  sudo apt install -y python3.10 python3.10-venv python3.10-dev
  
  echo "Python 3.10 успешно установлен!"
}

install_python_centos() {
  echo "Установка Python 3.10 на систему CentOS/RHEL..."
  sudo yum groupinstall "Development Tools" -y
  sudo yum install gcc openssl-devel bzip2-devel libffi-devel zlib-devel -y
  cd /tmp
  wget https://www.python.org/ftp/python/3.10.0/Python-3.10.0.tgz
  tar -xzf Python-3.10.0.tgz
  cd Python-3.10.0
  ./configure --enable-optimizations
  make altinstall
  
  echo "Python 3.10 успешно установлен!"
  cd "$original_dir"
}

install_python_mac() {
  echo "Установка Python 3.10 на macOS..."
  if ! command -v brew &>/dev/null; then
    echo "Homebrew не найден. Устанавливаем Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  fi
  brew install python@3.10
  echo "Python 3.10 успешно установлен!"
}

# Installing python packages
install_python_packages() {
  if [ -f "reqs.txt" ]; then
    echo "Установка Python-пакетов из файла reqs.txt..."
    python3 -m ensurepip --upgrade
    python3 -m pip install --upgrade -r reqs.txt
  else
    echo "Файл reqs.txt не найден. Пропускаем установку Python-пакетов."
  fi
}


# Installing python 
install_python() {
  if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if [ -f /etc/debian_version ]; then
      install_python_debian
      apt install -y tmux cron
    elif [ -f /etc/redhat-release ]; then
      install_python_centos
      yum install -y tmux cron
    else
      echo "Неизвестная система Linux. Установка не поддерживается."
    fi
  elif [[ "$OSTYPE" == "darwin"* ]]; then
    install_python_mac
  else
    echo "Система не поддерживается этим скриптом."
  fi
}

# installing dependencies
install_deps() {
  if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if [ -f /etc/debian_version ]; then
      apt install -y tmux cron
      sudo systemctl start cron
      sudo systemctl enable cron
    elif [ -f /etc/redhat-release ]; then
      yum install -y tmux cronie
      sudo systemctl start crond
      sudo systemctl enable crond
    else
      echo "Неизвестная система Linux. Установка не поддерживается."
    fi
  else
    echo "Система не поддерживается этим скриптом."
  fi
}
install_deps

# Checking python3 is exists
if command -v python3 &>/dev/null; then
    :
else
    echo "Python не установлен."

    install_python
    sudo ln -sf /usr/local/bin/python3.10 /usr/bin/python3
fi
install_python_packages

# Starting the server

start_tmux_session() {
    if tmux has-session -t $1 > /dev/null 2>&1; then
        :
    else
        tmux new -d -s $1 "cd $2 && $3"
    fi
}

start_tmux_session status "." "python3 server.py"

# Opening the port in the firewall

if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo ".env файл не найден. Использую порт 7879 по умолчанию."
    PORT=7879  # Порт по умолчанию, если файл .env не найден
fi

add_port_ufw() {
    echo "Используется UFW. Добавляем порт $PORT..."
    sudo ufw allow $PORT
    sudo ufw reload
    echo "Порт $PORT добавлен в разрешённые в UFW."
}

add_port_firewalld() {
    echo "Используется firewalld. Добавляем порт $PORT..."
    sudo firewall-cmd --permanent --add-port=$PORT/tcp
    sudo firewall-cmd --reload
    echo "Порт $PORT добавлен в разрешённые в firewalld."
}

add_port_iptables() {
    echo "Используется iptables. Добавляем порт $PORT..."
    sudo iptables -A INPUT -p tcp --dport $PORT -j ACCEPT
    sudo iptables-save > /etc/iptables/rules.v4
    echo "Порт $PORT добавлен в разрешённые в iptables."
}

if command -v ufw &>/dev/null; then
    add_port_ufw
elif command -v firewall-cmd &>/dev/null; then
    add_port_firewalld
elif command -v iptables &>/dev/null; then
    add_port_iptables
else
    echo "Не удалось определить установленный брандмауэр. Пожалуйста, установите UFW, firewalld или iptables."
    exit 1
fi



chmod +x autorun.sh
mkdir /etc/status | mv autorun.sh /etc/status/autorun.sh
mkdir /etc/status/config

cron_string='@reboot /bin/bash -li "/etc/status/autorun.sh"'
if ! crontab -l &>/dev/null; then
    echo "Crontab ещё не существует. Создаём новый..."
    crontab -l > /dev/null 2>&1
fi
(crontab -l | grep -Fxq "$cron_string") || (crontab -l; echo "$cron_string") | crontab -

echo "Строка добавлена в crontab."

/bin/bash -li "/etc/status/autorun.sh"