from functions import *
from game_processing import stop_game, start_game, set_room_timer

def setting_game_callback_analysing(message_id, user_id, chat_id, calldata_text):
    activity = ''
    text = ''
    markup = None
    password_existence, room_number = "", 0
    if calldata_text[:2] in ['C-', 'J4']:
        password_existence = calldata_text[2:]
    elif calldata_text != "J3":
        try:
            room_number = int(calldata_text[3:])
        except ValueError:
            room_number = calldata_text[3:]
            room_number = int(room_number[(room_number.find('/') + 1):])
    if calldata_text[:2] == 'C-':
        alarm_text, keyboard_text, buttons, keyboard_size, friends_request, room_number = creating_room(message_id, user_id, chat_id, password_existence)
        markup = create_inline_keyboard_markup(buttons, keyboard_size)
        ask_to_bot("send_message", chat_id, alarm_text, markup=turn_off_menu_butons())
        ask_to_bot("edit_message", chat_id, keyboard_text, message_id=message_id, markup=markup)
        if friends_request:
            send_message_to_all_users_friends(user_id, f"Користувач, що додав вас до друзів, створив кімнату, її номер {friends_request}.\nПриєднуйтесь до нього!!!")
    elif calldata_text[:2] == 'C1':
        sheriff_existence = check_certain_game_info(room_number, "sheriff")
        if sheriff_existence == 'disabled':
            game_info_delete(room_number, 'sheriff')
        else:
            game_info_add(room_number, 'sheriff', 'disabled')
        activity, text, markup = standart_returning_info(room_number, message_id, user_id)
    elif calldata_text[:2] == 'C2':
        doctor_existence = check_certain_game_info(room_number, "doctor")
        if doctor_existence == 'disabled':
            game_info_delete(room_number, 'doctor')
        else:
            game_info_add(room_number, 'doctor', 'disabled')
        activity, text, markup = standart_returning_info(room_number, message_id, user_id)
    elif calldata_text[:2] == 'C3':
        lady_existence = check_certain_game_info(room_number, "lady")
        if lady_existence == 'disabled':
            game_info_delete(room_number, 'lady')
        else:
            game_info_add(room_number, 'lady', 'disabled')
        activity, text, markup = standart_returning_info(room_number, message_id, user_id)
    elif calldata_text[:2] == 'C4':
        stop_game(room_number)
        activity = 'edit_message'
        text = 'Кімнату видалено'
        markup = None
    elif calldata_text[:2] == 'C5':
        is_started = start_game(room_number)
        if not is_started:
            activity = "ignore"
    elif calldata_text[:2] == "J1":
        if check_certain_game_info(room_number, "game_phase") != "preparing":
            text = "В цій кімнаті вже почалася гра"
            activity = "edit_message"
        elif len(check_certain_game_info(room_number, "people").strip(';').split(';')) >= 17:
            text = "В цій кімнаті вже максимальна кількість людей"
            activity = "edit_message"
        elif is_room_available(room_number):
            text = "В цій кімната вже завершилася гра"
            activity = "edit_message"
        elif check_certain_user_info(user_id, "in_room") == "False":
            if check_certain_game_info(room_number, "password") == "-":
                person_join(room_number, message_id, user_id, chat_id)
                text = create_keyboard_text(room_number, "preparing")
                refresh_all_keyboards_in_room(room_number, text)
                activity = 'ignore'
            else:
                change_certain_user_info(user_id, "in_room", f"typing_password/{room_number}|{message_id}")
                markup = create_inline_keyboard_markup([["Назад в меню", "J4"]])
                activity = "edit_message"
                text = "Напишіть пароль, щоб увійти в кімнату"
        else:
            activity = 'ignore'
    elif calldata_text[:2] == "J2":
        person_leave(room_number, user_id, message_id, chat_id)
        text = create_keyboard_text(room_number, "preparing")
        refresh_all_keyboards_in_room(room_number, text)
        activity = 'edit_message'
        text = 'Ви покинули кімнату'
        markup = None
    elif calldata_text == "J3":
        activity = "edit_message"
        text = "Ви не знайшли потрібної кімнати"
        ask_to_bot("send_message", chat_id, "Ми сподіваємося, що ви знайдете ще потрібну кімнату!", markup=turn_on_menu_butons())
    elif calldata_text == "J4":
        activity = "edit_message"
        text = "Ми сподіваємося, що ви знайдете ще потрібну кімнату!"
    return activity, text, markup

def standart_returning_info(room_number, message_id, user_id):
    text = create_keyboard_text(room_number)
    buttons = create_buttons(room_number, "admin")
    keyboard_size = 2
    activity = "edit_message"
    markup = create_inline_keyboard_markup(buttons, keyboard_size)
    return activity, text, markup

def creating_room(message_id, user_id, chat_id, password_existence="no"):
    if not is_in_room(user_id):
        room_number = find_room()
        if room_number:
            take_room(room_number)
            person_join(room_number, message_id, user_id, chat_id=chat_id)
            game_info_add(room_number, "admin", str(user_id))
            if password_existence == "no":
                password = '-'
            else:
                password = generate_password()
            if room_number:
                game_info_add(room_number, "password", password)
            alarm_text = f'Кімната створена\nЇї номер: {room_number}\n' + ("На кімнаті не встановлено пароля" if password == '-' else f"Пароль: {password}")
            buttons = create_buttons(room_number, "admin")
            keyboard_size = 2
            keyboard_text = "Ви є адміном цієї кімнати, тому налаштовуйте її:"
            friends_request = room_number
        else:
            alarm_text = "Будь ласка, зачайкате трохи та спробуйте ще раз"
            keyboard_text = 'Вибачте, але всі кімнати зайняті'
            buttons = []
            keyboard_size = 3
            friends_request = False
            room_number = None
        return alarm_text, keyboard_text, buttons, keyboard_size, friends_request, room_number
    else:
        alarm_text = 'Ви не можете створити кімнату, якщо ви вже знаходитеся в іншій!'
        keyboard_text = "Пасхалка!!!"
        buttons = []
        keyboard_size = 3
        return alarm_text, keyboard_text, buttons, keyboard_size, False, None

def join_room(message_id, user_id, chat_id):
    suitable_rooms = rooms_to_join()
    buttons = []
    if suitable_rooms == []:
        alarm_text = "На зараз, на жаль, нема кімнат для приєднання"
        keyboard_text = "Тому ми вам пропонуємо створити свою"
    else:
        alarm_text = "Бажаємо, вам приємної гри з друзями!!!"
        keyboard_text = 'Доступні кімнати:'
        buttons = []
        for room_number in suitable_rooms:
            buttons.append([f"Кімната №{room_number}", f"J1:{room_number}"])
        buttons.append(["Назад в меню", f"J3"])
    return alarm_text, keyboard_text, buttons, 1, False
