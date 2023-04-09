import time
import os

# This file need only for installing the bot on your pc (creating all necessity files).

print("Creating storage...")
print("Creating room's files...")
for room_number in range(1, 11):
    dir_path = os.path.join("Storage", "Rooms")
    path = os.path.join("Storage", "Rooms", f"room{room_number}")
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    with open(path, "w") as room_contain:
        room_contain.writelines(['game_phase:preparing\n',
                                 'password:\n',
                                 'keyboards:\n',
                                 'admin:\n',
                                 'people:\n',
                                 'spectators:\n'
                                 'mafia:\n',
                                 'sheriff:\n',
                                 'doctor:\n',
                                 'lady:\n'])


print("Creating rooms concierge")
dir_path = os.path.join("Storage", "Rooms")
path = os.path.join("Storage", "Rooms", "rooms_concierge")
if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
with open(path, "w") as room_contain:
    room_contain.writelines([f'room{index}:avaible\n' for index in range(1, 11)])


print("Creating allowed symbols file...")
dir_path = os.path.join("Storage")
path = os.path.join("Storage", f"Allowed_symbols")
if not os.path.isdir(dir_path):
    os.makedirs(dir_path)
with open(path, "w") as room_contain:
    room_contain.writelines(["QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm\n", "ЙЦУКЕНГШЩЗХЇФІВАПРОЛДЖЄЯЧСМИТЬБЮйцукенгшщзхїфівапролджєячсмитьбю\n", "1234567890-=+_\n"])


print("Creating 'user_files' directory...")
dir_path = os.path.join("Storage", "users_files")
if not os.path.isdir(dir_path):
    os.makedirs(dir_path)



print("Bot was successfully installed.\n\nDon`t forget to add 'TOKEN' in 'main.py'.")
time.sleep(10)