import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from files_operations import *
from main import ask_to_bot
from datetime import datetime

def create_inline_keyboard_markup(buttons, keyboard_width = 1):
    markup = InlineKeyboardMarkup(row_width=keyboard_width)
    for button in buttons:
        button_text = button[0]
        callback_data_text = button[1]
        markup.add(InlineKeyboardButton(text=button_text, callback_data=callback_data_text))
    return markup

def get_in_room(user_id):
    change_certain_user_info(user_id, 'in_room', 'True')

def is_in_room(user_id):
    room_condition = check_certain_user_info(user_id, 'in_room')
    if room_condition == 'True':
        return True
    else:
        return False

def turn_on_menu_butons():
    markup = ReplyKeyboardMarkup(row_width=2)
    markup.add(KeyboardButton("Опис всіх команд"), KeyboardButton("Створити кімнату"), KeyboardButton("Зайти в кімнату"), KeyboardButton("Про гру"), KeyboardButton("Друзі"), KeyboardButton("Налаштування аккаунту"))
    return markup

def turn_off_menu_butons():
    return ReplyKeyboardRemove()

def is_blocked(user_id):
    status = check_certain_user_info(user_id, 'status')
    if status == 'blocked':
        return True
    return False

def change_status(user_id, new_status):
    change_certain_user_info(user_id, 'status', new_status)

def person_join(room_number, message_id, user_id, chat_id = None):
    if chat_id == None:
        chat_id = check_certain_user_info(user_id, "chat_id")
    game_info_add(room_number, "keyboards", f"{chat_id}/{message_id};")
    game_info_add(room_number, "people", f"{user_id};")
    get_in_room(user_id)

def person_leave(room_number, user_id, message_id = None, chat_id = None, text_instead_keyboard = 'Кімнату покинуто'):
    if chat_id == None:
        chat_id = check_certain_user_info(user_id, "chat_id")
    if message_id == None:
        message_id = check_keyboard_message_id(room_number, user_id, chat_id)
    people = check_certain_game_info(room_number, 'people')
    people = people.replace(f"{user_id};", "")
    game_info_delete(room_number, "people")
    game_info_add(room_number, "people", people)
    keyboards = check_certain_game_info(room_number, 'keyboards')
    keyboards = keyboards.replace(f"{chat_id}/{message_id};", "")
    game_info_delete(room_number, "keyboards")
    game_info_add(room_number, "keyboards", keyboards)
    change_certain_user_info(user_id, 'in_room', 'False')
    ask_to_bot('edit_message', chat_id, text_instead_keyboard, message_id=message_id)
    ask_to_bot(activity="send_message", chat_id=chat_id, text="Давай зіграємо ще одну гру!", markup=turn_on_menu_butons())

def refresh_all_keyboards_in_room(room_number, text_on_keyboard, admin_exception = True, subgroup_exception = None, subgroup_text = ""):
    people = check_certain_game_info(room_number, "people").strip(';').split(';')
    if people == ['']:
        return None
    if admin_exception:
        admin = check_certain_game_info(room_number, "admin")
        people.remove(admin)
        chat_id = check_certain_user_info(admin, "chat_id")
        message_id = check_keyboard_message_id(room_number, admin, chat_id)
        buttons = create_buttons(room_number, "admin")
        markup = create_inline_keyboard_markup(buttons)
        refresh_keyboard(text_on_keyboard, chat_id, message_id, markup)
    if subgroup_exception:
        subgroup = check_certain_game_info(room_number, subgroup_exception).strip(';').split(';')
        for person in people:
            if person in subgroup:
                people.remove(person)
        for person in subgroup:
            chat_id = check_certain_user_info(person, "chat_id")
            message_id = check_keyboard_message_id(room_number, person, chat_id)
            buttons = create_buttons(room_number, subgroup_exception)
            markup = create_inline_keyboard_markup(buttons)
            refresh_keyboard(subgroup_text, chat_id, message_id, markup)
        for person in people:
            chat_id = check_certain_user_info(person, "chat_id")
            message_id = check_keyboard_message_id(room_number, person, chat_id)
            buttons = create_buttons(room_number)
            markup = create_inline_keyboard_markup(buttons)
            refresh_keyboard(text_on_keyboard, chat_id, message_id, markup)
    else:
        for person in people:
            chat_id = check_certain_user_info(person, "chat_id")
            message_id = check_keyboard_message_id(room_number, person, chat_id)
            buttons = create_buttons(room_number)
            markup = create_inline_keyboard_markup(buttons)
            refresh_keyboard(text_on_keyboard, chat_id, message_id, markup)

def refresh_keyboard(text, chat_id, message_id, markup=None):
    if not markup:
        ask_to_bot("edit_message", chat_id, text, message_id=message_id)
    else:
        ask_to_bot("edit_message", chat_id, text, message_id=message_id, markup=markup)


def check_keyboard_message_id(room_number, user_id, chat_id=None):
    if chat_id == None:
        chat_id = check_certain_user_info(user_id, "chat_id")
    keyboards = check_certain_game_info(room_number, "keyboards").strip(';')
    keyboards = keyboards[keyboards.find(str(chat_id)):]
    index = keyboards.find(';')
    keyboards = keyboards[:index] if index != -1 else keyboards
    message_id = keyboards[(keyboards.find('/') + 1):]
    return message_id

def create_keyboard_text(room_number, game_phase=None, role=None):
    text = ""
    people = check_certain_game_info(room_number, "people")
    if not game_phase:
        game_phase = check_certain_game_info(room_number, "game_phase")
    if game_phase == "preparing":
        people = check_certain_game_info(room_number, "people").strip(';').split(';')
        text = "Йде налаштування кімнати...\nКористувачі в кімнаті:\n"
        for person in people:
            moniker = check_certain_user_info(person, "moniker")
            text += str(moniker) + "\n"
        text += "\n" + "Замало людей для початку гри" if len(people) < 4 else "Готові почати"
    elif True:
        pass
    return text

def create_buttons(room_number, additional_info = None):
    game_phase = check_certain_game_info(room_number, "game_phase")
    people = check_certain_game_info(room_number, "people").strip(';').split(';')
    if not is_room_available(room_number):
        if game_phase == "preparing":
            if additional_info == "admin":
                buttons = [['Додати роль шерифа' if check_certain_game_info(room_number, "sheriff") else 'Видалити роль шерифа', f'C1:{room_number}'], ['Додати роль доктора' if check_certain_game_info(room_number, "doctor") else 'Видалити роль доктора', f'C2:{room_number}'], ['Додати роль леді' if check_certain_game_info(room_number, "lady") else 'Видалити роль леді', f'C3:{room_number}'], [f"Кількість мафії:{calculate_mafia_count(len(people))}", f"C6:{room_number}"], ['Видалити кімнату', f'C4:{room_number}'], ["Почати гру", f"C5:{room_number}"]]
            else:
                buttons = [["Покинути кімнату", f"J2:{room_number}"]]
        elif game_phase == "election_start":
            buttons = []
            for index, person in enumerate(people):
                moniker = check_certain_user_info(person, "moniker")
                buttons.append([F"Голосувати за {moniker}", f"G1:{person}/{room_number}"])
            buttons.append(["Пропустити голосування", f"G1:skip/{room_number}"])
        elif game_phase == "mafia_start":
            if additional_info == "mafia":
                buttons = []
                subgroup = check_certain_game_info(room_number, "mafia").strip(';').split(';')
                for person in people:
                    if person in subgroup:
                        people.remove(person)
                for index, person in enumerate(people):
                    moniker = check_certain_user_info(person, "moniker")
                    buttons.append([f"Хочу вбити {moniker}", f"G2:{person}/{room_number}"])
            else:
                buttons = []
        elif game_phase == "sheriff_start":
            buttons = []
            if additional_info == "sheriff":
                sheriff = check_certain_game_info(room_number, "sheriff")
                people.remove(sheriff)
                for person in people:
                    moniker = check_certain_user_info(person, "moniker")
                    buttons.append([f"Перевірити {moniker}", f"G3:{person}/{room_number}"])
        elif game_phase == "doctor_start":
            buttons = []
            if additional_info == "doctor":
                for person in people:
                    moniker = check_certain_user_info(person, "moniker")
                    buttons.append([f"Лікувати {moniker}", f"G4:{person}/{room_number}"])
        elif game_phase == "lady_start":
            buttons = []
            if additional_info == "lady":
                lady = check_certain_game_info(room_number, "lady")
                people.remove(lady)
                for person in people:
                    moniker = check_certain_user_info(person, "moniker")
                    buttons.append([f"Провести ніч з {moniker}", f"G5:{person}/{room_number}"])
        else:
            buttons = []
    else:
        buttons = []
    return buttons

def calculate_mafia_count(people_count):
    if people_count < 7:
        return 1
    elif people_count >= 7 and people_count <= 9:
        return 2
    elif people_count >= 10 and people_count <= 13:
        return 3
    elif people_count >= 14:
        return 4

def stop_all_rooms():
    for user_id in os.listdir(os.path.join("Storage", "users_files")):
        change_certain_user_info(user_id, "in_room", "False")
    for room_number in range(1, 11):
        if not is_room_available(room_number):
            exempt_room(room_number)
            try:
                refresh_all_keyboards_in_room(room_number, "Всі кімнати було закрито через помилку серверу", admin_exception=False, subgroup_exception="people", subgroup_text="Всі кімнати було закрито через помилку серверу")
            except telebot.apihelper.ApiTelegramException:
                pass
    return "All rooms was stopped successfully"

def result_votes(votes):
    votes = set(votes)
    result = {}
    for vote in votes:
        try:
            user_to_execute, voted_user = vote.split('/')
        except ValueError:
            continue
        result[user_to_execute] = result.get(user_to_execute) + 1 if result.get(user_to_execute) else 1
    max_number = 0
    user_id_to_execute = None
    for key, value in result.items():
        if max_number < value:
            user_id_to_execute = key
            max_number = value
    return user_id_to_execute, max_number

def make_spectator(room_number, user_id):
    game_info_add(room_number, "spectators", f"{user_id};")
    people = check_certain_game_info(room_number, "people").strip(';').split(';')
    people.remove(str(user_id))
    game_info_delete(room_number, "people")
    game_info_add(room_number, "people", ";".join(people))
    mafia = check_certain_game_info(room_number, "mafia").strip(';').split(';')
    if user_id in mafia:
        mafia.remove(user_id)
        game_info_delete(room_number, "mafia")
        game_info_add(room_number, "mafia", ";".join(mafia))
    sheriff = check_certain_game_info(room_number, "sheriff")
    if user_id == sheriff:
        game_info_add(room_number, "sheriff", ";died")
    doctor = check_certain_game_info(room_number, "doctor")
    if user_id == doctor:
        game_info_add(room_number, "doctor", ";died")
    lady = check_certain_game_info(room_number, "lady")
    if user_id == lady:
        game_info_add(room_number, "lady", ";died")
    chat_id = check_certain_user_info(user_id, "chat_id")
    message_id = check_keyboard_message_id(room_number, user_id, chat_id=chat_id)
    keyboards = check_certain_game_info(room_number, "keyboards").strip(';').split(';')
    keyboards.remove(f"{chat_id}/{message_id}")
    game_info_delete(room_number, "keyboards")
    game_info_add(room_number, "keyboards", ";".join(keyboards))
    change_certain_user_info(user_id, "in_room", "False")
    refresh_keyboard(text="Вас було вбито, тому ви були кікнути з кімнати", chat_id=chat_id, message_id=message_id)
    ask_to_bot("send_message", chat_id, "Не турбуйтеся, що вас вбили, наступного разу вдача буде на вашому боці!", markup=turn_on_menu_butons())

def delete_repeats_in_all_rooms():
    for room_number in range(1, 11):
        delete_repeats_in_room(room_number)

def delete_repeats_in_room(room_number):
    for type_of_info in ['game_phase', 'keyboards', 'admin', 'people', 'spectators', 'mafia', 'sheriff', 'doctor', 'lady']:
        string = check_certain_game_info(room_number, type_of_info)
        if '|' in string:
            game_info = string.strip('|').split('|')
            for certain_game_info in game_info:
                certain_game_info = certain_game_info.strip(';').split(';')
                certain_game_info = set(certain_game_info)
                game_info_delete(room_number, type_of_info)
                game_info_add(room_number, type_of_info, ";".join(certain_game_info))
        else:
            game_info = string.strip(';').split(';')
            game_info = set(game_info)
            game_info_delete(room_number, type_of_info)
            game_info_add(room_number, type_of_info, ";".join(game_info))

def logbook_update(logbook, user_id, max_size_of_logbook = 15):
    now = datetime.now()
    time = str(now)
    new_el = [user_id, time]
    if len(logbook) >= max_size_of_logbook:
        del logbook[0]
    logbook.append(new_el)
    return logbook

def check_spam(logbook, user_id, allowed_interval = 2, message_to_spam = 5):
    previous_date = ''
    previous_time = [0.0, 0.0, 0.0]
    spammed_times = 0
    for request in logbook:
        request_user_id = request[0]
        time = request[1]
        date, time = time.split(' ')
        time = time.split(':')
        time = [float(i) for i in time]
        if request_user_id == user_id:
            if date == previous_date:
                request_interval = abs(previous_time[0]*3600 + previous_time[1]*60 + previous_time[2] - time[0]*3600 - time[1]*60 - time[2])
                if request_interval < allowed_interval:
                    spammed_times += 1
            previous_date, previous_time = date, time
    return True if spammed_times > message_to_spam else False

def block_user(user_id):
    change_certain_user_info(user_id, "status", "blocked")

def users_friend_list(user_id):
    text = "Список ваших друзів:\n"
    friends = check_certain_user_info(user_id, "friends").strip(';').split(';')
    if friends != ['']:
        for friend in friends:
            text += friend + "\n"
    else:
        text = "На жаль, у вас нема друзів в боті"
    return text

def add_friend(id_who_adding, id_who_added):
    friends = check_certain_user_info(id_who_adding, "friends")
    friends += id_who_added + ";"
    change_certain_user_info(id_who_adding, "friends", friends)

def adding_new_friend(user_id, users_text):
    text = "Нема користувача з таким id! Попробуйте ще раз, або нажміть \"Назад\" на повідомленні з верху"
    if users_file_existence(users_text):
        add_friend(user_id, users_text)
        text = f"Ви додали користувача {users_text} до своїх друзів"
        change_certain_user_info(user_id, "in_room", "False")
    return text

def friend_list_in_buttons(user_id):
    buttons = []
    friends = check_certain_user_info(user_id, "friends").strip(';').split(';')
    if friends != ['']:
        for friend in friends:
            buttons.append([f"Видалити {friend}", f"F4:{friend}"])
    buttons.append(["Назад", "F"])
    return buttons

def delete_friend(user_id, selected_user_id):
    friends = check_certain_user_info(user_id, "friends")
    friends = friends.replace(selected_user_id + ';', '')
    change_certain_user_info(user_id, "friends", friends)

def logbook_delete_users_requests(logbook, user_id):
    for index, request in enumerate(logbook):
        if request[1] == user_id:
            del logbook[index]
    return logbook

def send_message_to_all_users_friends(user_id, text, markup = None):
    friends = check_certain_user_info(user_id, "friends").strip(';').split(';')
    if friends != []:
        for friend in friends:
            if friend:
                friend_chat_id = check_certain_user_info(friend, "chat_id")
                ask_to_bot("send_message", friend_chat_id, text, markup=markup)

def changing_moniker(user_id, new_moniker):
    new_moniker = remake_strings_to_allowed(new_moniker)[0]
    if len(new_moniker) > 20:
        new_moniker = new_moniker[:20]
    change_certain_user_info(user_id, "moniker", new_moniker)
    return new_moniker

def generate_password(length=6):
    symbol_string = "QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm1234567890"
    password = ""
    for _ in range(length):
        password += choice(symbol_string)
    return password
