# ddrosatom
Repository for rosatom hackaton
# Запуск приложения
После скачивания репозитория необходимо установить все зависимости:
```
 pip install -r requirements.txt
```
Провести миграции:
```
python manage.py makemigrations content
python manage.py makemigrations accounts
python manage.py makemigrations organizations
python manage.py migrate
```
Запустить сервер:
```
python manage.py runserver 0.0.0.0:8000
```
