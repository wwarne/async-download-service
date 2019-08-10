# Микросервис для скачивания файлов

Микросервис помогает работе основного сайта, сделанного на CMS и обслуживает
запросы на скачивание архивов с файлами. Микросервис не умеет ничего, кроме упаковки файлов
в архив. Закачиваются файлы на сервер через FTP или админку CMS.

Создание архива происходит на лету по запросу от пользователя. Архив не сохраняется на диске, вместо этого по мере упаковки он сразу отправляется пользователю на скачивание.

От неавторизованного доступа архив защищен хешом в адресе ссылки на скачивание, например: `http://host.ru/archive/3bea29ccabbbf64bdebcc055319c5745/`. Хеш задается названием каталога с файлами, выглядит структура каталога так:

```
- photos
    - 3bea29ccabbbf64bdebcc055319c5745
      - 1.jpg
      - 2.jpg
      - 3.jpg
    - af1ad8c76fda2e48ea9aed2937e972ea
      - 1.jpg
      - 2.jpg
```


## Как установить

Для работы микросервиса нужен Python версии не ниже 3.6.
Сервис использует [Poetry](https://poetry.eustace.io/) для управления зависимостями.

```bash
poetry install
```

## Как запустить

```bash
$ poetry shell - активация virtualenv
$ python server.py
```
или
```bash
poetry run python server.py
```

## Параметры сервиса

* -f, --folder, или переменная окружения DVMN_FOLDER - путь к основной директории с фотографиями;
* -l, --logs или переменная окружения DVMN_LOGS - вести логирование работы;
* -d, --delay или переменная окружения DVMN_DELAY - число секунд между отдачей клиенту порции архива;

Сервер запустится на порту 8080, чтобы проверить его работу перейдите в браузере на страницу [http://127.0.0.1:8080/](http://127.0.0.1:8080/).

Development with docker
-----------------------

To start development server inside ``docker`` you will need to run:

.. code:: bash

  docker-compose build
  docker-compose up
  
 Production configuration
------------------------

You will need to specify extra configuration
to run ``docker-compose`` in production.
Since production build also uses ``caddy``,
which is not required into the development build.

.. code:: bash

  docker-compose -f docker-compose.yml -f docker/docker-compose.prod.yml config > docker-compose.deploy.yml



## Как развернуть на сервере

```bash
python server.py
```

После этого перенаправить на микросервис запросы, начинающиеся с `/arhive/`. Например:

```
GET http://host.ru/archive/3bea29ccabbbf64bdebcc055319c5745/
GET http://host.ru/archive/af1ad8c76fda2e48ea9aed2937e972ea/
```

# Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).