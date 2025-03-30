# Бот для контроля понятийных знаний студентов

## Настройка окружения
Установите зависимости (из текущей директории):
```bash
pip install -r requirements.txt
```

Установить neo4j и Qwen 2.5.

### Настройка базы данных
Установка PostgreSQL:
```sh
sudo apt install postgresql
```

Конфигурирование PostgreSQL. В командной оболочке PostgreSQL(`sudo -u postgres psql`):
```psql
CREATE DATABASE ontologer;
\password postgres # Ввести пароль (aaaaaa)
```

Создание БД:
```sh
export PGPASSWORD=aaaaaa
psql -U postgres -d ontologer -a -f ./sql/create_db.sql
```
Если не сработало см. [Stack Overflow](https://stackoverflow.com/questions/69676009/psql-error-connection-to-server-on-socket-var-run-postgresql-s-pgsql-5432):.
В `/etc/postgresql/14/main/pg_ident.conf` добавить
```
# MAPNAME       SYSTEM-USERNAME         PG-USERNAME
user1           <computer-username>     postgres
```
В `sudo nano /etc/postgresql/14/main/pg_hba.conf` добавить
```
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             postgres                                trust
```

Терминал для доступа к базе данных:
```
psql -U postgres -d ontologer
```

### Перед запуском

Установите следующие переменные окружения:
* `BOT_TOKEN` - токен для доступа к боту Telegram (создаётся через [@BotFather](https://t.me/BotFather))
* `NEO4J_IP` - IP развёрнутой базы данных neo4j. *По умолчанию 'localhost'*
* `NEO4J_PORT` - порт развёрнутой базы данных neo4j. *По умолчанию '7687'*
* `NEO4J_USER` - пользователь развёрнутой базы данных neo4j. *По умолчанию 'neo4j'*
* `NEO4J_PWD` - пароль пользователя развёрнутой базы данных neo4j. *По умолчанию 'aaaaaa'*
* `DB_NAME` - имя развёрнутой базы данных PostgreSQL. *По умолчанию 'ontologer'*
* `DB_USER` - пользователь развёрнутой базы данных PostgreSQL. *По умолчанию 'postgres'*
* `DB_PWD` - пароль пользователя развёрнутой базы данных PostgreSQL. *По умолчанию 'aaaaaa'*
* `DB_HOST` - IP развёрнутой базы данных PostgreSQL. *По умолчанию 'localhost'*
* `DB_PORT` - порт развёрнутой базы данных PostgreSQL. *По умолчанию '5432'*

## Запуск
```bash
python3 bot.py
```
