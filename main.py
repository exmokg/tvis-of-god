# main.py

from telethon import TelegramClient, sync
from telethon.tl.functions.channels import JoinChannelRequest, InviteToChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.errors.rpcerrorlist import FloodWaitError
import time
import logging
from config import api_id_list, api_hash_list, phone_numbers, group_to_join, group_to_invite

# Настройка логирования
logging.basicConfig(filename='logs.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

clients = []

# Авторизация клиентов
for i in range(4):
    client = TelegramClient(f'session_{i}', api_id_list[i], api_hash_list[i])
    client.connect()
    if not client.is_user_authorized():
        client.send_code_request(phone_numbers[i])
        client.sign_in(phone_numbers[i], input(f'Enter the code for {phone_numbers[i]}: '))
    clients.append(client)

# Вступление в группы
for client in clients:
    try:
        group_entity = client(ImportChatInviteRequest(group_to_join.split('/')[-1]))
        client(JoinChannelRequest(group_entity))
        logging.info(f'Client {client.session.filename} joined group {group_to_join}')
    except Exception as e:
        logging.error(f'Failed to join group {group_to_join} with client {client.session.filename}: {e}')

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

# Инвайт пользователей в другую группу
index = 0
for user_id, username in user_data:
    client = clients[index % 4]
    try:
        group_entity = client(ResolveUsernameRequest(group_to_invite.split('/')[-1]))
        client(InviteToChannelRequest(group_entity, [user_id]))
        logging.info(f'Invited user {username} to group {group_to_invite}')
    except FloodWaitError as e:
        logging.warning(f'Flood wait error, sleeping for {e.seconds} seconds')
        time.sleep(e.seconds)
    except Exception as e:
        logging.error(f'Failed to invite user {username} with ID {user_id}: {e}')
    index += 1
    time.sleep(2)  # Задержка между инвайтами

# Завершение работы клиентов
for client in clients:
    client.disconnect()
