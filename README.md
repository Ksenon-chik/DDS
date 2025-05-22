# Barter Platform

Платформа для обмена вещами на Django.

---

## Требования

- Python 3.8+
- виртуальное окружение (venv или venv)
- Django 5.2+
- Django REST Framework
- django-filter
- pytest (для тестов)

---

## Установка

1. Склонировать репозиторий:

   ```bash
   git clone https://github.com/Ksenon-chik/DDS.git
   cd DDS


2. Создать и активировать виртуальное окружение:

    ```bash
    python -m venv .venv
    .venv\Scripts\activate     # Windows
    source .venv/bin/activate  # macOS/Linux
   

3. Установить зависимости:

    ```bash
   pip install -r requirements.txt
   

4. Применить миграции:

    ```bash
    python manage.py migrate
   

5. Создать суперпользователя:

    ```bash
   python manage.py createsuperuser
   

## Запуск

    python manage.py runserver


## Тестирование
    
    python manage.py test dds_app