import argparse
import os
import time

from dotenv import load_dotenv
import requests
import telegram
from telegram.ext import Updater


if __name__ == '__main__':
    load_dotenv()
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    devman_token = os.getenv('DEVMAN_TOKEN')
    parser = argparse.ArgumentParser(description='you should enter your chat id, you can get it here: https://t.me/userinfobot')
    parser.add_argument('chat_id', help='your chat id', type=int)
    chat_id = parser.parse_args().chat_id
    updater = Updater(token=telegram_token)
    bot = telegram.Bot(token=telegram_token)
    url = 'https://dvmn.org/api/long_polling/'
    headers = {'Authorization': f'Token {devman_token}'}
    params = None

    while True:
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            print('no connection')
            time.sleep(5)
            continue
        except requests.exceptions.RequestException:
            print('request exception')
            continue
        devman_checklist = response.json()
        if devman_checklist['status'] == 'found':
            new_attempts = devman_checklist['new_attempts']
            last_attempt_timestamp = devman_checklist['last_attempt_timestamp']
            params = {'timestamp': last_attempt_timestamp}
            lesson_title = new_attempts[0]['lesson_title']
            is_negative = new_attempts[0]['is_negative']
            if is_negative:
                attempt_status_message = 'К сожалению, в вашей работе нашлись ошибки.'
            else:
                attempt_status_message = 'Преподавателю всё понравилось, можно приступать к следующему уроку!'
            telegram_message = f'У вас проверили работу "{lesson_title}"\n\n {attempt_status_message}'
            bot.send_message(chat_id=chat_id, text=telegram_message)