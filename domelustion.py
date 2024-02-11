import json
import requests
from colorama import init, Fore
from telethon.sync import TelegramClient
from telethon.tl.types import ChannelParticipantsAdmins, ChannelParticipantsBots

# Initialize colorama
init()

def print_header(version, update_available):
    update_status = "Доступно обновление" if update_available else "Обновлений нет"
    print(
        Fore.BLUE
        + r"""
  ____                       _           _   _             
 |  _ \  ___  _ __ ___   ___| |_   _ ___| |_(_) ___  _ __  
 | | | |/ _ \| '_ ` _ \ / _ \ | | | / __| __| |/ _ \| '_ \ 
 | |_| | (_) | | | | | |  __/ | |_| \__ \ |_| | (_) | | | |
 |____/ \___/|_| |_| |_|\___|_|\__,_|___/\__|_|\___/|_| |_|
                                                            
    """
        + Fore.YELLOW
        + f"Версия: {version}"
        + Fore.RESET
        + "\n"
        + Fore.RED
        + f"Статус: {update_status}"
        + Fore.RESET
        + "\n"
        + Fore.GREEN
        + "Разработчик: https://github.com/BitixDev"
        + Fore.RESET
    )

# Введите свои данные API
api_id = ''
api_hash = ''

async def remove_interacted_bots(client):
    async for dialog in client.iter_dialogs():
        if dialog.is_user and dialog.entity.bot:
            print(f"Удаляем бота '{dialog.entity.first_name}' (ID: {dialog.entity.id}) из личных сообщений")
            await client.delete_dialog(dialog.entity.id)
    print("Боты, с которыми вы взаимодействовали, успешно удалены.")

async def main(client):
    await client.start()

    # Load version info from GitHub
    response = requests.get('https://raw.githubusercontent.com/BitixDev/Domelustion/main/Version.json')
    if response.status_code == 200:
        version_data = response.json()
        print_header(version_data.get('version', 'Неизвестно'), version_data.get('update_available', False))
    else:
        print("Не удалось загрузить данные о версии и обновлениях.")

    me = await client.get_me()
    print("\nВы вошли в аккаунт:")
    print(f"Имя пользователя: {me.username}")
    print(f"ID: {me.id}")

    while True:
        print("\nВыберите действие:")
        print("1. Очистить чаты (чаты, в которых вы не администратор и нет других участников)")
        print("2. Выход из каналов (в которых вы не владелец)")
        print("3. Удалить ботов с аккаунта")
        print("4. Удалить всех ботов из личных сообщений и заблокировать их")
        print("5. Выйти из аккаунта")
        choice = input("Введите номер выбранного действия: ")

        if choice == '1':
            await clear_non_admin_chats(client)
        elif choice == '2':
            await leave_non_owner_channels(client)
        elif choice == '3':
            await remove_bots(client)
        elif choice == '4':
            await remove_interacted_bots(client)
        elif choice == '5':
            await client.log_out()
            print("Вы успешно вышли из аккаунта.")
            break
        else:
            print("Неверный ввод. Попробуйте снова.")

async def clear_non_admin_chats(client):
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            admins = await client.get_participants(dialog, filter=ChannelParticipantsAdmins)
            if len(admins) == 1:
                print(f"Очищаем чат '{dialog.name}' (ID: {dialog.id})")
                await client.delete_dialog(dialog.id)
        elif dialog.is_channel:
            participants = await client.get_participants(dialog, filter=ChannelParticipantsBots)
            if len(participants) == 0:
                print(f"Очищаем канал '{dialog.name}' (ID: {dialog.id})")
                await client.delete_dialog(dialog.id)

    print("Чаты успешно очищены.")

async def leave_non_owner_channels(client):
    async for dialog in client.iter_dialogs():
        if dialog.is_channel and not dialog.entity.creator:
            print(f"Покидаем канал '{dialog.name}' (ID: {dialog.id})")
            await client.delete_dialog(dialog.id)

    print("Вы успешно вышли из каналов, в которых вы не являетесь владельцем.")

if __name__ == "__main__":
    with TelegramClient('session_name', api_id, api_hash) as client:
        client.loop.run_until_complete(main(client))
