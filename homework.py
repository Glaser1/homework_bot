import os
import sys
import time
import requests
import exceptions
import logging

from dotenv import load_dotenv

import telegram

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log',
    filemode='w',
    format='%(asctime)s, %(levelname)s, %(message)s'
)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 5
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправка сообщения в Telegram-чат."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.info(f' Бот отправил сообщение: {message}')
    except exceptions.UnableToSendMessage(
            f'Ошибка при отправке сообщения: {message}'
    ) as error:
        logging.error(error)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=error)
        logging.info(f' Бот отправил сообщение: {error}')


def get_api_answer(current_timestamp):
    """Запрос к API-сервису."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code != 200:
        logging.error(
            f'Эндпоит недоступен: Код ответа API: {response.status_code}'
        )
        raise exceptions.UnexpectedStatusCode()
    try:
        return response.json()
    except Exception as error:
        logging.info(f' Сбой при запросе к эндпоинту {error}')


def check_response(response):
    """Проверка ответа API."""
    if not isinstance(response, dict):
        logging.error('Ответ API не соответствует ожидаемому')
        raise TypeError
    if not isinstance(response.get('homeworks'), list):
        logging.error('Ответ API не соответствует ожидаемому')
        raise KeyError
    try:
        return response.get('homeworks')
    except KeyError:
        logging.error('Несуществующий ключ')


def parse_status(homework):
    """Получение статуса конкретной домашней работы."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if 'homework_name' not in homework.keys():
        logging.error('Несуществующий ключ')
        raise KeyError
    if 'status' not in homework.keys():
        logging.error('Несуществующий ключ')
        raise KeyError
    if homework_status not in HOMEWORK_STATUSES:
        logging.error('Несуществующий ключ')
        raise KeyError
    verdict = HOMEWORK_STATUSES.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка переменных окружения."""
    if TELEGRAM_TOKEN and PRACTICUM_TOKEN and TELEGRAM_CHAT_ID:
        return True
    else:
        logging.critical('Отсутствует переменная окружения')
        return False


def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    while True:
        try:
            response = get_api_answer(163163153)
            check = check_response(response)
            status = check[0].get('status')
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            send_message(bot, message)
            time.sleep(RETRY_TIME)
        else:
            response2 = get_api_answer(163163153)
            check2 = check_response(response2)
            status2 = check2[0].get('status')
            if status != status2:
                send_message(bot, parse_status(check2[0]))
            else:
                logging.debug('Отсутствие в ответе нового статуса')
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
