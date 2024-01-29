Для работы приложения нужно:
1. Собрать контейнер:
> docker build -t sbl_web_prn .
2. Указать в .env имя_пользователя, пароль, ip_dhcp_сервера, порт_winrm, OUI_mac-addr_принтеров
3. Создать сеть в docker с именем noc_prod:
> docker network create --subnet 10.233.1.0/24 --ip-range 10.233.1.0/24 --driver=bridge -o com.docker.network.bridge.name=noc_prod noc_prod
4. Собрать docker compose:
> docker compose up -d
5. При необходимости, поместить за реверс прокси (в моем примере traefik2.0)