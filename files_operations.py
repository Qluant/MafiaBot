import os
from random import choice

def file_read(path):
    with open(path, "r") as certain_file:
        file_contain = certain_file.readlines()
        file_contain = [line.strip() for line in file_contain]
    return file_contain

def return_allowed_symbols():
    return "".join(file_read(os.path.join("Storage", "Allowed_symbols")))

def generate_name():
    sides = ["Mafia", "Civilian", "Sheriff", "Doctor", "Lady", "Joker", "Mayor", "Don", "Hermit", "Loner"]
    action = [" killer", " of this city", " lover", " in soul", "'s first enemy", " hater"]
    return choice(sides) + choice(action)

def remake_strings_to_allowed(*args):
    new_made_strings = []
    allowed_symbols = return_allowed_symbols()
    for string in args:
        new_made_string = ""
        if not string:
            string = ""
        for symbol in string:
            if symbol in allowed_symbols:
                new_made_string += symbol
        if new_made_string.strip() == "":
            new_made_string = generate_name()
        new_made_strings.append(new_made_string)
    return new_made_strings

def users_file_existence(user_id):
    if not user_id in os.listdir(os.path.join("Storage", "users_files")):
        return False
    return True

def create_new_users_file(user_id, user_nickname, user_last_name, user_name, chat_id, user_status = "regular"):
    user_nickname, user_last_name, user_name = remake_strings_to_allowed(user_nickname, user_last_name, user_name)
    moniker = ""
    if user_nickname:
        moniker = user_nickname
    elif user_name:
        moniker = user_name
    else:
        moniker = user_last_name
    user_nickname, user_last_name, user_name, moniker = remake_strings_to_allowed(user_nickname, user_last_name, user_name, moniker)
    with open(os.path.join("Storage", "users_files", f"{user_id}"), 'w') as users_file:
        users_file.writelines([f"id:{user_id}\n",
                               f"nickname:{user_nickname}\n",
                               f"last_name:{user_last_name}\n",
                               f"first_name:{user_name}\n",
                               f"moniker:{moniker}\n",
                               f"status:{user_status}\n",
                               f"chat_id:{chat_id}\n",
                               f"in_room:False\n",
                               f"statistics:\n",
                               f"friends:\n"
                               f"spams:0"])

def check_user_info(user_id):
    user_info = file_read(os.path.join("Storage", "users_files", f"{user_id}"))
    user_info = [certain_user_info.strip().split(':') for certain_user_info in user_info]
    returning_info = {}
    for key in user_info:
        value = key[1]
        key = key[0]
        returning_info[key] = value
    return returning_info

def check_certain_user_info(user_id, type_of_info):
    user_info = check_user_info(user_id)
    info = user_info.get(type_of_info)
    return info if info else ''

def change_certain_user_info(user_id, type_of_info, new_info):
    user_info = check_user_info(user_id)
    collection_size = len(user_info)
    with open(os.path.join("Storage", "users_files", f"{user_id}"), 'w') as user_file:
        index = 0
        for key, value in user_info.items():
            if key == type_of_info:
                if collection_size == index:
                    user_file.write(f'{key}:{new_info}')
                else:
                    user_file.write(f'{key}:{new_info}\n')
            elif collection_size == index:
                user_file.write(f'{key}:{value}')
            else:
                user_file.write(f'{key}:{value}\n')
            index += 1

def find_room():
    with open(os.path.join("Storage", "Rooms", "rooms_concierge"), "r") as rooms_concierge:
        rooms_availability = rooms_concierge.readlines()
    rooms_availability = [room_availability.strip() for room_availability in rooms_availability]
    room_number = None
    for number, room_availability in enumerate(rooms_availability):
        if room_availability[(room_availability.find(':') + 1):] == "available":
            room_number = number + 1
            break
    return room_number

def take_room(room_number):
    with open(os.path.join("Storage", "Rooms", "rooms_concierge"), "r") as rooms_concierge:
        rooms_availability = rooms_concierge.readlines()
    for index, line in enumerate(rooms_availability):
        if f'room{room_number}' in line:
            rooms_availability[index] = f'room{room_number}:taked\n'
            break
    with open(os.path.join("Storage", "Rooms", "rooms_concierge"), "w") as rooms_concierge:
        rooms_concierge.writelines(rooms_availability)
    with open(os.path.join("Storage", "Rooms", f"room{room_number}"), "w") as room_contain:
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

def exempt_room(room_number):
    with open(os.path.join("Storage", "Rooms", "rooms_concierge"), "r") as rooms_concierge:
        rooms_availability = rooms_concierge.readlines()
    for index, line in enumerate(rooms_availability):
        if f'room{room_number}' in line:
            rooms_availability[index] = f'room{room_number}:available\n'
            break
    with open(os.path.join("Storage", "Rooms", "rooms_concierge"), "w") as rooms_concierge:
        rooms_concierge.writelines(rooms_availability)

def check_game_info(room_number):
    user_info = file_read(os.path.join("Storage", "Rooms", f"room{room_number}"))
    user_info = [certain_user_info.strip().split(':') for certain_user_info in user_info]
    returning_info = {}
    for key in user_info:
        try:
            value = key[1]
        except IndexError:
            value = ''
        key = key[0]
        returning_info[key] = value
    return returning_info

def check_certain_game_info(room_number, type_of_info):
    game_info = check_game_info(room_number)
    info = game_info.get(type_of_info)
    return info if info else ''

def game_info_add(room_number, type_of_info, info):
    file_contain = file_read(os.path.join("Storage", "Rooms", f"room{room_number}"))
    for index, line in enumerate(file_contain):
        if type_of_info == line[:(line.find(':'))]:
            file_contain[index] = line + info + '\n'
        else:
            file_contain[index] = file_contain[index] + '\n'
    with open(os.path.join("Storage", "Rooms", f"room{room_number}"), "w") as room_info:
        room_info.writelines(file_contain)

def game_info_delete(room_number, type_of_info):
    file_contain = file_read(os.path.join("Storage", "Rooms", f"room{room_number}"))
    for index, line in enumerate(file_contain):
        if type_of_info == line[:(line.find(':'))]:
            file_contain[index] = type_of_info + ':' + '\n'
        else:
            file_contain[index] = file_contain[index] + '\n'
    with open(os.path.join("Storage", "Rooms", f"room{room_number}"), "w") as room_info:
        room_info.writelines(file_contain)

def add_phase_info(room_number, info):
    file_contain = file_read(os.path.join("Storage", "Rooms", f"room{room_number}"))
    file_contain.reverse()
    for index, line in enumerate(file_contain):
        if 'day' in line or 'night' in line:
            file_contain[index] = line.strip() + ';' + info + '\n'
    file_contain.reverse()
    with open(os.path.join("Storage", "Rooms", f"room{room_number}"), "w") as room_info:
        room_info.writelines(file_contain)

def rooms_to_join():
    suitable_rooms = []
    with open(os.path.join("Storage", "Rooms", "rooms_concierge"), "r") as rooms_concierge:
        rooms_availability = rooms_concierge.readlines()
    for index, line in enumerate(rooms_availability):
        if f'taked' in line:
            game_phase = check_certain_game_info(index + 1, "game_phase")
            people = check_certain_game_info(index + 1, "people").strip(';').split(';')
            if game_phase == "preparing" and len(people) < 17:
                suitable_rooms.append(index + 1)
    return suitable_rooms

def add_game_new_info_type(room_number, type_of_info):
    with open(os.path.join("Storage", "Rooms", f"room{room_number}"), "r") as certain_file:
        file_contain = certain_file.readlines()
    file_contain.append(type_of_info + ':\n')
    with open(os.path.join("Storage", "Rooms", f"room{room_number}"), "w") as room_info:
        room_info.writelines(file_contain)

def check_day_number(room_number):
    file_contain = file_read(os.path.join("Storage", "Rooms", f"room{room_number}"))
    file_contain.reverse()
    number = 0
    for line in file_contain:
        if "day_" in line or "night_" in line:
            type_of_info = line[:line.find(':')]
            number = type_of_info[(type_of_info.find('_') + 1):]
            break
    return number

def is_room_available(room_number):
    with open(os.path.join("Storage", "Rooms", "rooms_concierge"), "r") as rooms_concierge:
        rooms_availability = rooms_concierge.readlines()
    rooms_availability = [room_availability.strip() for room_availability in rooms_availability]
    for room in rooms_availability:
        if str(room_number) in room:
            if "available" in room:
                return True
            else:
                return False
