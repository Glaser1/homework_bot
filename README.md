# homework_bot

Телеграм-бот для проверки статуса домашней работы.

### Бот умеет:
 * раз в 10 минут опрашивать API сервиса Практикум.Домашка и проверять статус отправленной на ревью домашней работы;
 * при обновлении статуса анализировать ответ API и отправлять вам соответствующее уведомление в Telegram;
 * логировать свою работу и сообщать вам о важных проблемах сообщением в Telegram.

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Glaser1/homework_bot.git
```

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source venv/Scripts/activate
```

```
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Создать .env-файл со строками:

``` PRACTICUM_TOKEN = <Токен вашего Яндекс.Практикум аккаунта> ```

``` TELEGRAM_TOKEN = <Токен вашего telegram-бота> ```

``` TELEGRAM_CHAT_ID = <id вашего telegram-аккаунта> ```

Запустить проект:

```
python manage.py runserver
```
