from functions import *
from room_setup import setting_game_callback_analysing, join_room
from game_processing import in_game_calldata_analysing

def text_analysing(message):
    if not is_blocked(message.from_user.id):
        text = message.text.strip()
        if text not in menu_buttons:
            return 'Вибачте, я вас не розумію(((', "", turn_on_menu_butons() if not is_in_room(message.from_user.id) else turn_off_menu_butons(), False, False
        elif is_in_room(message.from_user.id):
            return 'Ви не можете переходити в інші режими під час гри', "", None, False, False
        else:
            try:
                alarm_text, buttons, keyboard_size = menu_buttons.get(text)
                if alarm_text == "account":
                    moniker = check_certain_user_info(message.from_user.id, "moniker")
                    alarm_text = f"Ваш id: {message.from_user.id}\nВаше прізвисько зараз: {moniker}"
                markup = create_inline_keyboard_markup(buttons, keyboard_width=keyboard_size)
                keyboard_text = ''
                delete_menu_buttons_necessity = False
                friends_request = False
            except TypeError:
                operation = menu_buttons.get(text)
                alarm_text, keyboard_text, buttons, keyboard_size, friends_request = operation(message.id, message.from_user.id, message.chat.id)
                delete_menu_buttons_necessity = True
                markup = create_inline_keyboard_markup(buttons, keyboard_width=keyboard_size)
            return alarm_text, keyboard_text, markup, delete_menu_buttons_necessity, friends_request

def callback_analysing(message_id, user_id, calldata_text):
    chat_id = check_certain_user_info(user_id, 'chat_id')
    text = ''
    markup = None
    activity = ''
    if calldata_text == 'F':
        change_certain_user_info(user_id, "in_room", "False")
        activity = 'edit_message'
        text = 'Виберіть, що вам потрібно'
        markup = create_inline_keyboard_markup([['Додати друга', 'F1'], ['Видалити друга', 'F2'], ['Список друзів', 'F3']], keyboard_width=2)
    elif calldata_text == 'F1':
        change_certain_user_info(user_id, "in_room", "adding_new_friend")
        activity = 'edit_message'
        text = 'Напишіть id користувача, щоб додати його в друзі'
        markup = create_inline_keyboard_markup([['Назад', 'F']])
    elif calldata_text == 'F2':
        activity = 'edit_message'
        buttons = friend_list_in_buttons(user_id)
        text = 'Ваші друзі, виберіть кого ви хочете видалити:' if buttons != [["Назад", "F"]] else "На жаль, у вас нема друзів в боті"
        markup = create_inline_keyboard_markup(buttons=buttons)
    elif calldata_text == 'F3':
        activity = 'edit_message'
        text = users_friend_list(user_id)
        markup = create_inline_keyboard_markup([['Назад', 'F']])
    elif calldata_text[:2] == 'F4':
        selected_user_id = calldata_text[(calldata_text.find(':') + 1):]
        delete_friend(user_id, selected_user_id)
        activity = 'edit_message'
        text = f"Користувача {selected_user_id} видалено зі списку друзів"
        markup = create_inline_keyboard_markup([['Назад', 'F2']])
    elif calldata_text == 'A':
        change_certain_user_info(user_id, "in_room", "False")
        activity = 'edit_message'
        moniker = check_certain_user_info(user_id, "moniker")
        text = f"Ваш id: {user_id}\nВаше прізвисько зараз: {moniker}"
        markup = create_inline_keyboard_markup([["Змінити прізвисько", "A1"]])
    elif calldata_text[:2] == 'A1':
        change_certain_user_info(user_id, "in_room", "changing_moniker")
        activity = 'edit_message'
        text = 'Напишіть своє нове прізвисько\n(Увага, всі смайлики заборонені в прізвеську, тому я їх видалю з прізьвиська та довжина повинна бути менша 20 символів)'
        markup = create_inline_keyboard_markup([['Назад', 'A']])
    elif calldata_text[0] == 'C' or calldata_text[0] == 'J':
        activity, text, markup = setting_game_callback_analysing(int(message_id), user_id, chat_id, calldata_text)
    elif calldata_text[0] == 'G':
        activity, text, markup = in_game_calldata_analysing(int(message_id), user_id, chat_id, calldata_text)
    return activity, chat_id, message_id, text, markup

help_text = "Створити кімнату/Зайти в кімнату - один користувач створює кімнату і налаштовує її, всі інші заходять в кімнату перед цим прочитайте Про гру"

about_game_text = "Для чого потрібен бот?\n\nЯкщо вам хочется пограти в компанії мафію, але ніхто не хоче бути ведучим, або у вас нема карт мафія, то вам сюди. Тут ви зможете зручно пограти в мафія всією компанією!\n\nЯк грати в нашому боту в мафію?\n\nДля цього вам потрібно бути на зв'язку, або поряд один з одними та всім бути підключиними до бота. І так, одна людина створює кімнату та налаштовує її, тим часом всі інші заходять до нього в кімнату (по номеру). Про самі правила мафії можете почитати по посиланню:\nhttps://kava.ua/uk/news/pravila-igry-v-mafiyu-rolevuyu"

menu_buttons = {
    "Опис всіх команд": [help_text, [], 1],
    "Створити кімнату": ["Потрібно створювати пароль на вході в кімнату?", [["Так", "C-yes"], ["Ні", "C-no"]], 2],
    "Зайти в кімнату": join_room,
    "Про гру": [about_game_text, [], 1],
    "Друзі": ['Виберіть, що вам потрібно', [['Додати друга', 'F1'], ['Видалити друга', 'F2'], ['Список друзів', 'F3']], 2],
    "Налаштування аккаунту": ["account", [["Змінити прізвисько", "A1"]], 1]
}
