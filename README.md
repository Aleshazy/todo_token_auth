# TODO API

Простой проект: список задач с входом по токену.

Что умеет:
- регистрация
- вход
- создание задач
- просмотр задач
- смена статуса задачи
- удаление завершенной задачи

Как запустить:
1. Установить Docker
2. В папке проекта выполнить команду:

docker compose up --build

После запуска:
- API: http://localhost:8000
- Документация: http://localhost:8000/docs

Главные роуты:
- POST /register
- POST /login
- GET /todos
- POST /todos

CI/CD:
- В проекте добавлен GitHub Actions workflow: `.github/workflows/ci.yml`
- Он запускается на `push` и `pull_request` в `main`/`master`
- Сборка выполняет установку зависимостей, проверку Python синтаксиса и сборку Docker-образа

Cloudflare Tunnel:
- Для публичного доступа к локальному приложению используйте `cloudflared`
- Установите Cloudflare Tunnel на своей машине: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/
- Запустите приложение локально:

  `docker compose up --build`

- Создайте именованный туннель (если еще не сделали):

  `cloudflared tunnel create todo-tunnel`

- Сохраните `TUNNEL_ID`, который Cloudflare выведет при создании.
- В Cloudflare DNS добавьте запись CNAME для домена или поддомена:

  `your-domain.com CNAME <TUNNEL_ID>.cfargotunnel.com`

- Пример конфигурации лежит в `.cloudflared/config.yml`.
  Замените `<TUNNEL_ID>`, `<ваш_пользователь>`, `<имя_домена>` на свои значения.

- Затем запустите туннель так:

  `cloudflared tunnel run todo-tunnel`

- После запуска трафик вашего домена будет направлен на локальный `http://localhost:8000`.

Если домен уже настроен, но туннель "пустой":
1. Убедитесь, что в Cloudflare DNS есть CNAME на `<TUNNEL_ID>.cfargotunnel.com`.
2. Убедитесь, что `cloudflared` запущен на машине с вашим приложением.
3. Убедитесь, что локально доступен порт `8000`.

Важно:
- В проекте менять код не нужно, туннель работает на уровне сети и DNS.
- Файл `.cloudflared/config.yml` содержит маршрутизацию от домена на локальный порт.
