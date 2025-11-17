# ddrosatom
Repository for rosatom hackaton
# Проект в фирме
https://www.figma.com/design/FxgPcn99zoblYj4nbPzSpH/%D1%85%D0%B0%D0%BA%D0%B0%D1%82%D0%BE%D0%BD?node-id=0-1&t=2MFD5oGf7upR0JCe-1
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

