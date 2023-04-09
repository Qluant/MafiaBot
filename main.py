import telebot
from telebot import TeleBot

from bot_processing import *

# There is must be your telegram token
bot = TeleBot('your_token')

logbook = []
logbook_size = 50
allowed_interval = 1

@bot.message_handler(commands=['start'])
def start(message):
    if not users_file_existence(message.from_user.id):
        create_new_users_file(message.from_user.id, message.from_user.username, message.from_user.last_name, message.from_user.first_name, message.chat.id)
    if not is_blocked(message.from_user.id):
        global logbook
        logbook = logbook_update(logbook, message.from_user.id, max_size_of_logbook=logbook_size)
        anti_spam(message.from_user.id)
        markup = turn_on_menu_butons() if not is_in_room(message.from_user.id) else turn_off_menu_butons()
        bot.send_message(message.chat.id, f'Привіт, {check_certain_user_info(message.from_user.id, "moniker")}, я бот в якому ти зможешь грати в мафію з друзями!\nДля всіх деталей нажми "Опис всіх команд" та "Про гру" нижче', reply_markup=markup)

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, help_text, reply_markup=turn_on_menu_butons())

@bot.message_handler(content_types=['text'])
def textMessageHandler(message):
    if not is_blocked(message.from_user.id):
        global logbook
        logbook = logbook_update(logbook, message.from_user.id, max_size_of_logbook=logbook_size)
        anti_spam(message.from_user.id)
        if is_blocked(message.from_user.id):
            return None
        user_room = check_certain_user_info(str(message.from_user.id), "in_room")
        if user_room == "adding_new_friend" and not message.text in menu_buttons:
            text = adding_new_friend(str(message.from_user.id), message.text)
            bot.send_message(message.chat.id, text)
        elif user_room == "changing_moniker" and not message.text in menu_buttons:
            new_moniker = changing_moniker(str(message.from_user.id), message.text)
            bot.send_message(message.chat.id, f"Ваше прізвисько змінено!\nТепер воно:\n{new_moniker}")
            change_certain_user_info(message.from_user.id, "in_room", "False")
        elif "typing_password" in user_room and not message.text in menu_buttons:
            room_number = user_room.replace("typing_password/", "")
            room_number, message_id = room_number.split("|")
            if message.text == check_certain_game_info(room_number, "password"):
                person_join(room_number, message_id, message.from_user.id, message.chat.id)
                text = create_keyboard_text(room_number, "preparing")
                refresh_all_keyboards_in_room(room_number, text)
                ask_to_bot("send_message", message.chat.id, "Ви війшли в кімнату!!!\nДивітся в повідомленні више кімнату!")
            else:
                ask_to_bot("send_message", message.chat.id, "Невірний пароль!!!\nСпробуйте ще раз, або нажміть зверху \"Назад в меню\":")
        else:
            if user_room in ["adding_new_friend", "changing_moniker"]:
                change_certain_user_info(message.from_user.id, "in_room", "False")
            alarm_text, keyboard_text, markup, delete_menu_buttons_necessity, friends_request = text_analysing(message)
            if delete_menu_buttons_necessity:
                bot.send_message(message.chat.id, alarm_text, reply_markup=turn_off_menu_butons())
                bot.send_message(message.chat.id, keyboard_text, reply_markup=markup)
            else:
                bot.send_message(message.chat.id, alarm_text, reply_markup=markup)
            if friends_request:
                send_message_to_all_users_friends(message.from_user.id, f"Користувач, що додав вас до друзів, створив кімнату, її номер {friends_request}.\nПриєднуйтесь до нього")

@bot.callback_query_handler(func=lambda call: True)
def callbackQueryHandler(call):
    message_id, user_id, callback_text = call.message.message_id, call.from_user.id, call.data
    if not is_blocked(user_id):
        global logbook
        logbook = logbook_update(logbook, user_id, max_size_of_logbook=logbook_size)
        anti_spam(user_id)
        activity, chat_id, message_id, text, markup = callback_analysing(message_id, user_id, callback_text)
        if not activity == "ignore":
            ask_to_bot(activity, chat_id, text, markup=markup, message_id=message_id)

def ask_to_bot(activity, chat_id, text, markup=None, message_id=None):
    if activity == "send_message":
        bot.send_message(chat_id, text, reply_markup=markup)
    elif activity == "edit_message":
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=markup)

def anti_spam(user_id):
    global logbook, allowed_interval
    if check_spam(logbook, user_id, allowed_interval=allowed_interval, message_to_spam=10):
        times_spammed = int(check_certain_user_info(user_id, "spams"))
        if times_spammed > 2:
            block_user(user_id)
            print(f"Було заблоковано користувача {user_id} за спам")
            bot.send_message(chat_id=check_certain_user_info(user_id, "chat_id"), text="Вас було заблоковано!\nПричина: спам")
        else:
            times_spammed += 1
            change_certain_user_info(user_id, "spams", times_spammed)
            print(f"Видано попередження користувачу {user_id} за спам")
            bot.send_message(chat_id=check_certain_user_info(user_id, "chat_id"), text="Не спамьте, або ми вас забанимо!!!")

def main():
    stop_all_rooms()
    print("Bot starts polling...")
    bot.polling(none_stop=True, interval=0)

if __name__ == '__main__':
    main()
