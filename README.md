# TODO API

Что умеет:
- регистрация
- вход
- создание задач
- просмотр задач
- смена статуса задачи
- удаление завершенной задачи

Как запустить:
python -m uvicorn main:app --reload

Главные роуты:
- POST /register
- POST /login
- GET /todos
- POST /todos