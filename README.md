## Установка

### 1. Клонируем проект

sudo git clone -b production https://github.com/cloudsucker/kinohubble.git /opt/kinohubble

### 2. Кладём deploy.sh

cd /opt/kinohubble
chmod +x deploy.sh

### 3. Первый запуск (сам создаст сервис и запустит)

./deploy.sh
