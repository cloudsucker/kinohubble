## Установка

### 1. Клонируем проект

```bash
sudo git clone -b production https://github.com/cloudsucker/kinohubble.git /opt/kinohubble
```

### 2. Кладём deploy.sh

```bash
cd /opt/kinohubble
sudo chmod +x deploy.sh
```

### 3. Первый запуск (сам создаст сервис и запустит)

```bash
sudo apt install python3.12-venv
sudo ./deploy.sh
```
