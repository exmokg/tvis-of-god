# parse_users.py

from telethon import TelegramClient, sync
from telethon.tl.functions.contacts import ResolveUsernameRequest
import logging
from config import api_id_list, api_hash_list, phone_numbers, group_to_join

# Настройка логирования
logging.basicConfig(filename='logs.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

clients = []

# Авторизация клиентов
for i in range(1):
    client = TelegramClient(f'session_{i}', api_id_list[i], api_hash_list[i])
    client.connect()
    if not client.is_user_authorized():
        client.send_code_request(phone_numbers[i])
        client.sign_in(phone_numbers[i], input(f'Enter the code for {phone_numbers[i]}: '))
    clients.append(client)

# Парсинг участников группы
user_data = []
for client in clients:
    try:
        group_entity = client(ResolveUsernameRequest(group_to_join.split('/')[-1]))
        participants = client.get_participants(group_entity)
        for participant in participants:
            user_data.append((participant.id, participant.username))
            logging.info(f'Found user {participant.username} with ID {participant.id}')
    except Exception as e:
        logging.error(f'Failed to parse users from group {group_to_join} with client {client.session.filename}: {e}')

# Запись данных в файл
with open('users.txt', 'w') as file:
    for user_id, username in user_data:
        file.write(f'{user_id}, {username}\n')

# Завершение работы клиентов
for client in clients:
    client.disconnect()
