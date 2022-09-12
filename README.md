# Учебный проект Yatube

Социальная сеть с возможностью создания, просмотра, редактирования и удаления (CRUD) записей. Реализован механизм подписки на понравившихся авторов и отслеживание их записей. Покрытие тестами. Реализована возможность добавления изображений.

![Stack Overflow](https://img.shields.io/badge/-Stackoverflow-FE7A16?style=for-the-badge&logo=stack-overflow&logoColor=white)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-0078d7.svg?style=for-the-badge&logo=visual-studio-code&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)

## _Запуск_:
- Клонируйте репозиторий:
```sh
git clone https://github.com/aimerkz/hw05_final.git
```
- Установка зависимостей:
```sh
pip install -r requirements.txt
```
- Применение миграций:
```sh
python manage.py makemigrations
python manage.py migrate
```
- Создание администратора:
```sh
python manage.py createsuperuser
```
- Запуск приложения:
```sh
python manage.py runserver
```
