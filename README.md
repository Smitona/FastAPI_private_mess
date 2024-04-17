# Сервис для отправки сообщений пользователям

### API, который позволяет:
1. Отправить сообещения пользователю.
2. Поменять настройки профиля.
3. Найти пользователя по его usename

Авторизация по username и паролю с jwt токеном.

## Запуск проекта:
1. Клонировать репозиторий
    ```
    git clone git@github.com:Smitona/messenger-FastAPI.git
    ```
2. Перейти в директорию проекта и создать env. файл с переменные по примеру env_example. Установить виртуальное окружение и зависимости:
    ```
    cd messenger-FastAPI
    ```
    ```
    py -3.11 -m venv venv
    ```
    ```
    source venv/Scripts/Activate
    ```
    ```
    pip install -r requirements.txt
    ```
3. Перейти в папку с файлом main.py и запустить проект:
   ```
   cd app/
   ```
   ```
   uvicorn main:app --reload
   ```

Документацию можно будет открыть по ссылке [http://127.0.0.1:8000/docs#](http://127.0.0.1:8000/docs#)

---
### Стек ⚡
<img src="https://img.shields.io/badge/Python-black?style=for-the-badge&logo=Python&logoColor=DodgerBlue"/> <img src="https://img.shields.io/badge/-FastAPI-white?style=for-the-badge&logo=fastapi&logoColor=#009688"/>
<img src="https://img.shields.io/badge/-MongoDB-black?style=for-the-badge&logo=MongoDB&logoColor=#47A248"/>
