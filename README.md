# Yatube_project

## Социальная сеть

### Описание

Даёт возможность:

- просматривать чужие публикации (без регистрации)
- зарегестрироваться на сайте (личный кабинет)
- управлять своими публикациями на сайте: создавать, редактировать, удалять (текст и картинка)
- просматривать, добавлять комментарии, а так же редактировать свои
- подписываться на авторов, просматривать и искать их публикации

### Технологии

Python 3.7

Django 2.2.16

Pillow 8.3.1

Sorl_thumbnail 12.7.0

Django_debug_toolbar 3.2.4

SQLite 3.21.0

### Как запустить проект в dev-режиме

Клонировать репозиторий и перейти в него в командной строке:

```bash
git clone https://github.com/sonikk666/yatube

cd yatube
```

Cоздать и активировать виртуальное окружение:

```bash
python3 -m venv env

source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```bash
python3 -m pip install --upgrade pip

pip install -r requirements.txt
```

Выполнить миграции:

```bash
python3 yatube/manage.py migrate
```

Запустить проект:

```bash
python3 yatube/manage.py runserver
```

### Автор

Никита Михайлов
