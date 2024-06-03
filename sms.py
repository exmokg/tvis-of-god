# main.py

from telethon import TelegramClient, sync
from telethon.tl.functions.messages import SendMessageRequest
from telethon.errors.rpcerrorlist import FloodWaitError, UsernameNotOccupiedError
import time
import logging
from config import api_id_list, api_hash_list, phone_numbers

# Настройка логирования
logging.basicConfig(filename='logs.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

clients = []

# Авторизация клиентов
for i in range(4):
    client = TelegramClient(f'session_{i}', api_id_list[i], api_hash_list[i])
    client.connect()
    if not client.is_user_authorized():
        client.send_code_request(phone_numbers[i])
        client.sign_in(phone_numbers[i], input(f'Введите код для {phone_numbers[i]}: '))
    clients.append(client)

# Чтение данных пользователей из файла
usernames = []
with open('usernames.txt', 'r') as file:
    for line in file:
        usernames.append(line.strip())

# Отправка сообщений пользователям
message = "Привет! есть движуха одна актуально для города и для Оша будем подымать минимум 500$ в неделю! ни сома не надо вкладывать,только работать и всё,ты как в деле?"
index = 0
for username in usernames:
    client = clients[index % 4]
    try:
        client.send_message(username, message)
        logging.info(f'Скинули нахуй сообщение ёбаному {username}')
    except UsernameNotOccupiedError:
        logging.error(f'Ёбанный {username} не существует')
    except FloodWaitError as e:
        logging.warning(f'Flood wait error, спим {e.seconds} секунд')
        time.sleep(e.seconds)
    except Exception as e:
        logging.error(f'Не удалось отправить сообщение ёбанному {username}: {e}')
    index += 1
    if index % 2 == 0:  # Смена аккаунта после отправки 2 сообщений
        time.sleep(2)  # Задержка между отправкой сообщений

# Завершение работы клиентов
for client in clients:
    client.disconnect()
