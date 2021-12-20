import os
import sys
import time
import requests
import exceptions
import logging

from dotenv import load_dotenv

from telegram import Bot

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

tokens = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]

RETRY_TIME = 600
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


def get_api_answer(current_timestamp):
    """Запрос к API-сервису."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}

    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != 200:
            logging.info('Статус-код ответа отличается от ожидаемого')
            raise exceptions.UnexpectedStatusCode
        return response.json()
    except TypeError as error:
        logging.error(error)


def check_response(response):
    """Проверка ответа API."""
    if not isinstance(response, dict):
        logging.error('Ответ API не соответствует ожидаемому')
        raise TypeError
    if not isinstance(response.get('homeworks'), list):
        logging.error('Ответ API не соответствует ожидаемому')
        raise KeyError
    try:
        return response['homeworks']
    except KeyError:
        logging.error('Несуществующий ключ')


def parse_status(homework):
    """Получение статуса конкретной домашней работы."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if 'homework_name' not in homework:
        logging.error('Несуществующий ключ')
        raise KeyError
    if 'status' not in homework:
        logging.error('Несуществующий ключ')
        raise KeyError
    if homework_status not in HOMEWORK_STATUSES:
        logging.error('Несуществующий ключ')
        raise KeyError
    verdict = HOMEWORK_STATUSES.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка переменных окружения."""
    if all(tokens):
        return True
    logging.critical('Отсутствует переменная окружения')
    return False


def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = Bot(token=TELEGRAM_TOKEN)
    start_review_stamp = 1630443600
    response = get_api_answer(start_review_stamp)
    check = check_response(response)
    status = check[0]['status']
    while True:
        try:
            response = get_api_answer(start_review_stamp)
            check = check_response(response)
            if check[0]['status'] != status:
                status = check[0]['status']
                send_message(bot, parse_status(check[0]))
            else:
                logging.debug('Отсутствие в ответе нового статуса')
                send_message(bot,
                             'Отсутствие в работе нового статуса'
                             )
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
