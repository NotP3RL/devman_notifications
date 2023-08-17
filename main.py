import argparse
import json
import os

from dotenv import load_dotenv
import requests
import telegram
from telegram.ext import Updater


if __name__ == '__main__':
    load_dotenv()
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    DEVMAN_TOKEN = os.getenv('DEVMAN_TOKEN')
    parser = argparse.ArgumentParser(description='you should enter your chat id, you can get it here: https://t.me/userinfobot')
    parser.add_argument('chat_id', help='your chat id', type=int)
    chat_id = parser.parse_args().chat_id
    updater = Updater(token=TELEGRAM_TOKEN)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)

    while True:
        try:
            params = {}
            try:
                if deserialized_response['status'] == 'timeout':
                    params.update({'timestamp': deserialized_response['timestamp_to_request']})
            except NameError:
                pass
            headers = {'Authorization': f'Token {DEVMAN_TOKEN}'}
            response = requests.get('https://dvmn.org/api/long_polling/', headers=headers, params=params)
            response.raise_for_status()
            deserialized_response = json.loads(response.text)
            if deserialized_response['status'] == 'found':
                for attempt in deserialized_response['new_attempts']:
                    if attempt['is_negative']:
                        attempt_status_message = 'К сожалению, в работе нашлись ошибки.'
                    else:
                        attempt_status_message = 'Преподавателю всё понравилось, можно приступать к следующему уроку!'
                    telegram_message = f'У вас проверили работу "{attempt["lesson_title"]}"\n\n {attempt_status_message}'
                    bot.send_message(chat_id=chat_id, text=telegram_message)
        except (requests.exceptions.ConnectTimeout, ConnectionError):
            print('skill issue')
