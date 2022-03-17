# Простой Flask-апп, демонстрирующий REST API


## Установка

Нужен python 3.6+ (меньше не проверял).

```shell
pip install -r requirements.txt
```

## Настройка СУБД

Из папки, содержащей app.py:
```shell
flask db init
flask db migrate
flask db upgrade
```

Будет создана SQLite-база в папке выше, app.db.
При модификации моделей SQLAlchemy последние две команды надо выполнить еще раз.


## Запуск

Из папки, содержащей app.py:

```shell
flask run
```

## Эндпойнты

Для теста рекомендую Postman (app для Chrome).

### Список снэпшотов
GET http://127.0.0.1:5000/snapshots
Доп. аргументы ниже по вкусу, в любой комбинации.

#### Пагинация
GET http://127.0.0.1:5000/snapshots?start=5&limit=8

#### Сортировка
GET http://127.0.0.1:5000/snapshots?sort=name

#### Фильтрация
GET http://127.0.0.1:5000/snapshots?filter=id&fvalue=3


### Новый снэпшот
POST http://127.0.0.1:5000/snapshots

```json
{"name": "test1"}
```

### Новый блок данных
POST http://127.0.0.1:5000/datum

```json
{"id":345}
```

### Обновление снэпшота
PUT http://127.0.0.1:5000/snapshots/1

```json
{
    "datum": [],
    "id": 2,
    "name": "test222"
}
```

### Блоки данных снэпшота
GET http://127.0.0.1:5000/snapshots/1/datum

### Изменить блоки данных снэпшота
PUT http://127.0.0.1:5000/snapshots/1/datum

```json
[  {
        "id": 345
}]
```

### Очистить блоки данных снэпшота
DELETE http://127.0.0.1:5000/snapshots/1/datum
