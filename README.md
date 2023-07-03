# **EZTask**

# BUILT-IN
- **Python 3.11 + asyncio;**
- **FastAPI + SQLAlchemy + Pydantic + Alembic;**
- **PostgreSQL (psycopg2 + asyncpg);**
- Pytest;
- Redis;
- FastAPI-cache (based on Redis);
- Unicorn (debug mode) / gunicorn server.

# TODO
- Some simple, minimalistic, light visual interpretation (e.g. Telegram Bot or mobile app).

# ABOUT
The project realized some simple ideas. For starting work with it, user should, first of all, register and login (by getting and sending JWT-token).
Then:
- User can create note with choosing note date that he want;
- After it, user can manage him notes by any way: viewing with sorting/filters, editing, deleting, etc.;
- Note has any of two types: standard "note" or optional "task" ("task" can to be completed or not);
- For every active user app will generate random poll for the day. Service will ask him about **ONE** of param (preferring at evening time):
    - Health and feelings of the day;
    - Mood;
    - Expectations (negative/positive) from next day;
    - Taking helps from notes in current day;
    - Doing tasks he planned for today;
    - etc... (may be extended in future).
- By visual app (e.g. Telegram bot) user will take the poll and easy type it by just clicking one of button ("yes"/"no", "good"/"bad", etc.). Or do it manually for **ALL** params that included for possible day polling;
- Then, user could see reports and statistics about him days, him life, etc...;
- Advanced statistic viewing can be non-free (paid) function in future.

# USAGE
- Clone the repository;
- Run commands _*docker-compose build*_ and _*docker-compose up*_ from directory;
- Wait for the databases and application initialization processes (gunicorn server);
- After completing just check the Swagger UI docs using url: _**localhost:8080/docs**_;
- Test how it works! Recommended for using: _**'Postman'**_/_**'Insomnia'**_.

# NOTICE
- Authorization process doesn't work correctly on standard Swagger-docs app page, because by default Swagger authorization form includes _'**username**'_ and _'**password**'_ fields, but currently app use **email** instead of username. So, if you'll try to authorize by email using username field, you'll get an error, because authorization functions (checking form data, creating JWT Bearer Token, etc.) are expecting for _'**email**'_ form field.
- By this reason, you can test Auth-funcs just using Postman, etc.

# **RUS**
# TODO
- Простая, минималистичная, легкая визуальная интерпретация (например, Telegram-бот или мобильное приложение).

# ABOUT
В проекте реализовано несколько простых идей. Чтобы начать работу с ним, пользователь должен, прежде всего, зарегистрироваться и войти в систему (получив и отправив JWT-токен).
Затем:
- Пользователь может создать заметку, выбрав нужную ему дату заметки (большую либо равную текущей дате);
- После этого пользователь может управлять своими заметками любым способом: просматривать с сортировкой / фильтрами, редактировать, удалять и т.д.;
- Заметка может быть любого из двух типов: стандартная "заметка" или "задача" ("задача" может быть выполнена или нет).;
- Для каждого активного пользователя приложение сгенерирует случайный опрос дня. Визуальное приложение спросит его об **ОДНОМ** из параметров (предпочтительно в вечернее время):
    - Здоровье и самочувствие в текущий день;
    - Настроение;
    - Ожидания (негативные/позитивные) от следующего дня;
    - Получение помощи от заметок в текущий день;
    - Выполнение задач, поставленных на сегодня;
    - и так далее... (список может быть расширен в будущем).
- С помощью визуального приложения (например, Telegram-бота) пользователь примет участие в опросе, просто нажав кнопку ("да"/"нет", "плохо"/"хорошо" и т.д.). Или сделает это вручную для **ВСЕХ** параметров, которые есть для возможного дневного опроса;
- После этого пользователь может увидеть отчеты и статистику о своих днях, своей жизни и т.д...;
- Расширенный просмотр статистики в будущем может стать несвободной (платной) функцией.

# USAGE
- Клонируйте репозиторий;
- Запустите команды _*docker-compose build*_ и _*docker-compose up*_ из каталога;
- Дождитесь завершения процессов инициализации баз данных и приложений (сервер gunicorn);
- После завершения просто просмотрите документацию Swagger UI, используя url: _**'localhost:8080/docs'**_;
- Проверьте, как это работает! Рекомендуется к использованию: _**"Postman"**_/_**'Insomnia'**_.

# NOTICE
- Процесс авторизации некорректно работает на стандартной странице приложения Swagger-docs, поскольку по умолчанию форма авторизации Swagger включает поля _'**имя пользователя**'_ и _'**пароль**'_, но в настоящее время приложение использует ** адрес электронной почты ** вместо имени пользователя. Итак, если вы попытаетесь авторизоваться по электронной почте, используя поле username, вы получите сообщение об ошибке, поскольку функции авторизации (проверка данных формы, создание токена на предъявителя JWT и т.д.) ожидают _'**email**'_ поле формы.
- По этой причине вы можете протестировать Auth-функции, просто используя Postman и т.д.