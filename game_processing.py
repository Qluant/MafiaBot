from threading import Timer
from functions import *
from random import choice
from main import bot

def role_give(room_number, mafia_count, sheriff_existence = True, doctor_existence = True, lady_existence = True):
    people = check_certain_game_info(room_number, 'people').strip(';').split(';')
    for index in range(mafia_count):
        new_mafia_id = choice(people)
        people.remove(new_mafia_id)
        if index == mafia_count - 1:
            game_info_add(room_number, 'mafia', new_mafia_id)
            break
        game_info_add(room_number, 'mafia', new_mafia_id + ';')
    if sheriff_existence:
        sheriff_id = choice(people)
        game_info_add(room_number, 'sheriff', sheriff_id)
        people.remove(sheriff_id)
    if doctor_existence:
        doctor_id = choice(people)
        game_info_add(room_number, 'doctor', doctor_id)
        people.remove(doctor_id)
    if lady_existence:
        lady_id = choice(people)
        game_info_add(room_number, 'lady', lady_id)
        people.remove(lady_id)

def report_players_role(room_number):
    people_ids = check_certain_game_info(room_number, 'people').strip(';').split(';')
    mafia_ids = check_certain_game_info(room_number, 'mafia').split(';')
    sheriff_id = check_certain_game_info(room_number, 'sheriff')
    doctor_id = check_certain_game_info(room_number, 'doctor')
    lady_id = check_certain_game_info(room_number, 'lady')
    for mafia_id in mafia_ids:
        chat_id = check_certain_user_info(mafia_id, 'chat_id')
        bot.send_message(chat_id, 'Ви частина мафії цього міста!!!' if len(mafia_ids) > 1 else 'Ви є мафією цього міста')
        people_ids.remove(mafia_id)
    if sheriff_id != 'disabled':
        chat_id = check_certain_user_info(sheriff_id, 'chat_id')
        bot.send_message(chat_id, 'Ви шериф цього міста!!!')
        people_ids.remove(sheriff_id)
    if doctor_id != 'disabled':
        chat_id = check_certain_user_info(doctor_id, 'chat_id')
        bot.send_message(chat_id, 'Ви доктор цього міста!!!')
        people_ids.remove(doctor_id)
    if lady_id != 'disabled':
        chat_id = check_certain_user_info(lady_id, 'chat_id')
        bot.send_message(chat_id, 'Ви леді цього міста!!!')
        people_ids.remove(lady_id)
    for civilian_id in people_ids:
        chat_id = check_certain_user_info(civilian_id, 'chat_id')
        bot.send_message(chat_id, 'Ви є звичайним мешканцем цього міста!')
    phase_dispatcher(room_number)

def phase_dispatcher(room_number, previous_text=""):
    game_phase = check_certain_game_info(room_number, "game_phase")
    if game_phase == "role_giving":
        mafia_count = calculate_mafia_count(len(check_certain_game_info(room_number, "people").strip(';').split(';')))
        sheriff_existence = False if check_certain_game_info(room_number, 'sheriff') == 'disabled' else True
        doctor_existence = False if check_certain_game_info(room_number, 'doctor') == 'disabled' else True
        lady_existence = False if check_certain_game_info(room_number, 'lady') == 'disabled' else True
        game_info_delete(room_number, "game_phase")
        game_info_add(room_number, "game_phase", "discuss")
        role_give(room_number, mafia_count, sheriff_existence, doctor_existence, lady_existence)
        report_players_role(room_number)
    elif game_phase == "discuss":
        refresh_all_keyboards_in_room(room_number, "Початок дискусії\nУ вас є 5 хвилин перед голосуванням", admin_exception=False)
        game_info_delete(room_number, "game_phase")
        game_info_add(room_number, "game_phase", "election_start")
        set_room_timer(5, room_number)
        #set_room_timer(300, room_number)
    elif game_phase == "election_start":
        day_number = int(check_day_number(room_number)) + 1
        add_game_new_info_type(room_number, f"day_{day_number}")
        previous_text += "\nПочаток голосування\nВиберіть людину, яку хочете казнити, у вас є на це 30 секунд!"
        refresh_all_keyboards_in_room(room_number, previous_text, admin_exception=False)
        game_info_delete(room_number, "game_phase")
        game_info_add(room_number, "game_phase", "election_result")
        set_room_timer(30, room_number)
    elif game_phase == "election_result":
        day_number = check_day_number(room_number)
        votes = check_certain_game_info(room_number, f"day_{day_number}").strip(';').split(';')
        votes = make_missed_votes(room_number, "day", day_number, votes)
        executed_user_id, vote_count = result_votes(votes)
        if int(day_number) > 1:
            if check_certain_game_info(room_number, "lady") != "disabled":
                lady_result, nothing = check_night_action_result(room_number, "lady", previous_day=True)
                if lady_result == str(executed_user_id):
                    refresh_all_keyboards_in_room(room_number, f"Підсумок голосування:\nНайбільша кількість голосів ({vote_count}) припала на користувача {executed_user_id}, але цієї ночі ймоу було надано алібі від леді, томі його не буде страчено.\nПочинаеться ніч, всі йдуть до своїх домівок" if executed_user_id != "skip" else f"Підсумок голосування:\nНайбільша кількість голосів ({vote_count}) припала на пропуск цього голосування, тому нікого не було страчено...\nПочинаеться ніч, всі йдуть до своїх домівок", admin_exception=False)
                    day_result = False
                else:
                    refresh_all_keyboards_in_room(room_number, f"Підсумок голосування:\nНайбільша кількість голосів ({vote_count}) припала на користувача {executed_user_id}, тому його було страчено...\nПочинаеться ніч, всі йдуть до своїх домівок" if executed_user_id != "skip" else f"Підсумок голосування:\nНайбільша кількість голосів ({vote_count}) припала на пропуск цього голосування, тому нікого не було страчено...\nПочинаеться ніч, всі йдуть до своїх домівок", admin_exception=False)
                    if executed_user_id != "skip":
                        make_spectator(room_number, executed_user_id)
                    day_result, who_win = is_game_over(room_number)
            else:
                refresh_all_keyboards_in_room(room_number, f"Підсумок голосування:\nНайбільша кількість голосів ({vote_count}) припала на користувача {executed_user_id}, тому його було страчено...\nПочинаеться ніч, всі йдуть до своїх домівок" if executed_user_id != "skip" else f"Підсумок голосування:\nНайбільша кількість голосів ({vote_count}) припала на пропуск цього голосування, тому нікого не було страчено...\nПочинаеться ніч, всі йдуть до своїх домівок", admin_exception=False)
                if executed_user_id != "skip":
                    make_spectator(room_number, executed_user_id)
                day_result, who_win = is_game_over(room_number)
        else:
            refresh_all_keyboards_in_room(room_number, f"Підсумок голосування:\nНайбільша кількість голосів ({vote_count}) припала на користувача {executed_user_id}, тому його було страчено...\nПочинаеться ніч, всі йдуть до своїх домівок" if executed_user_id != "skip" else f"Підсумок голосування:\nНайбільша кількість голосів ({vote_count}) припала на пропуск цього голосування, тому нікого не було страчено...\nПочинаеться ніч, всі йдуть до своїх домівок", admin_exception=False)
            if executed_user_id != "skip":
                make_spectator(room_number, executed_user_id)
            day_result, who_win = is_game_over(room_number)
        if day_result:
            game_info_delete(room_number, "game_phase")
            game_info_add(room_number, "game_phase", "game_over")
        else:
            game_info_delete(room_number, "game_phase")
            game_info_add(room_number, "game_phase", "mafia_start")
        set_room_timer(5, room_number)
    elif game_phase == "mafia_start":
        night_number = int(check_day_number(room_number))
        add_game_new_info_type(room_number, f"night_{night_number}")
        refresh_all_keyboards_in_room(room_number, "Прокидається мафія і вибирає свою наступну жертву...", admin_exception=False, subgroup_exception="mafia", subgroup_text="Прокидається мафія та ви починаєте обирати свою наступну жертву\nВиберіть людину, яку хочете вбити, у вас є на це 30 секунд!")
        game_info_delete(room_number, "game_phase")
        game_info_add(room_number, "game_phase", "mafia_result")
        set_room_timer(30, room_number)
    elif game_phase == "mafia_result":
        refresh_all_keyboards_in_room(room_number, "Мафія зробивши свою справу, розходится", admin_exception=False)
        night_number = int(check_day_number(room_number))
        votes = check_certain_game_info(room_number, f"night_{night_number}").strip(';').split(';')
        votes = make_missed_votes(room_number, "night", night_number, votes, subgroup="mafia")
        executed_user_id, vote_count = result_votes(votes)
        game_info_add(room_number, f"night_{night_number}", f"-{executed_user_id}/{vote_count}")
        game_info_delete(room_number, "game_phase")
        game_info_add(room_number, "game_phase", "sheriff_start")
        game_info_add(room_number, f"night_{night_number}", "|")
        phase_dispatcher(room_number)
    elif game_phase == "sheriff_start":
        sheriff = check_certain_game_info(room_number, "sheriff")
        if sheriff == "disabled":
            game_info_delete(room_number, "game_phase")
            game_info_add(room_number, "game_phase", "doctor_start")
            phase_dispatcher(room_number)
            return None
        elif "died" in sheriff:
            refresh_all_keyboards_in_room(room_number, "А тим часом прокидається шериф і перевіряє якусь людину...", admin_exception=False)
        else:
            refresh_all_keyboards_in_room(room_number, "А тим часом прокидається шериф і перевіряє якусь людину...", admin_exception=False, subgroup_exception="sheriff", subgroup_text="Ви прокидаєтеся і йдете темним, порожнім містом\nДоходячи до жилого массива вам потрібно обрати кого ви хочете перевірити в цей раз, але у вас на це мало часу!\nТому виберайте скоріше:")
        game_info_delete(room_number, "game_phase")
        game_info_add(room_number, "game_phase", "sheriff_end")
        set_room_timer(25, room_number)
    elif game_phase == "sheriff_end":
        sheriff = check_certain_game_info(room_number, "sheriff")
        people = check_certain_game_info(room_number, "people").strip(';').split(';')
        if not check_night_action(room_number, "sheriff"):
            if sheriff != "disabled" and "died" not in sheriff:
                people.remove(sheriff)
                selected_person = choice(people)
                mafia = check_certain_game_info(room_number, "mafia").strip(';').split(';')
                is_mafia = True if selected_person in mafia else False
                moniker = check_certain_user_info(selected_person, "moniker")
                text = f"Ви перевіряете {moniker}\nРезультат: " + ("Він є членом мафії" if is_mafia else "Він не є мафією")
                night_number = check_day_number(room_number)
                game_info_add(room_number, f"night_{night_number}", "s|" + selected_person + '/' + ("Yes" if is_mafia else "No") + '|')
                chat_id = check_certain_user_info(sheriff, "chat_id")
                message_id = check_keyboard_message_id(room_number, sheriff, chat_id=chat_id)
                ask_to_bot("edit_message", chat_id, text, message_id=message_id)
        game_info_delete(room_number, "game_phase")
        game_info_add(room_number, "game_phase", "doctor_start")
        set_room_timer(5, room_number)
    elif game_phase == "doctor_start":
        doctor = check_certain_game_info(room_number, "doctor")
        if doctor == "disabled":
            game_info_delete(room_number, "game_phase")
            game_info_add(room_number, "game_phase", "lady_start")
            phase_dispatcher(room_number)
            return None
        elif "died" in doctor:
            refresh_all_keyboards_in_room(room_number, "Шериф повертається додому, вже з більшою інформацією, ніж в нього була до цього.\n На темних вулицях міста знову стає темно і тихо, але цю тишу переривають шаги доктора, його дешеві чоботи всі в багнюці. Він спішить комусь надати медичну допомогу...", admin_exception=False)
        else:
            refresh_all_keyboards_in_room(room_number, "Шериф повертається додому, вже з більшою інформацією, ніж в нього була до цього.\n На темних вулицях міста знову стає темно і тихо, але цю тишу переривають шаги доктора, його дешеві чоботи всі в багнюці. Він спішить комусь надати медичну допомогу...", admin_exception=False, subgroup_exception="doctor", subgroup_text="Виберіть людину, якій ви хочете надати першу медичну допомогу!\nВона може скоро померти, тому виберайте скоріше:")
        game_info_delete(room_number, "game_phase")
        game_info_add(room_number, "game_phase", "doctor_end")
        set_room_timer(25, room_number)
    elif game_phase == "doctor_end":
        doctor = check_certain_game_info(room_number, "doctor")
        people = check_certain_game_info(room_number, "people").strip(';').split(';')
        if not check_night_action(room_number, "doctor"):
            if doctor != "disabled" and "died" not in doctor:
                people.remove(doctor)
                selected_person = choice(people)
                mafia_choice, selected_mafia_count = check_night_action_result(room_number, "mafia")
                is_heal = True if selected_person == mafia_choice else False
                text = f"Ви надаете медичну допомогу {selected_person}\nРезультат: " + "Ви вилікували жертву мафії" if is_heal else "Ви не вилікували жертву мафії"
                night_number = check_day_number(room_number)
                moniker = check_certain_user_info(selected_person, "moniker")
                game_info_add(room_number, f"night_{night_number}", "d|" + moniker + '/' + ("Yes" if is_heal else "No") + '|')
                chat_id = check_certain_user_info(doctor, "chat_id")
                message_id = check_keyboard_message_id(room_number, doctor, chat_id=chat_id)
                ask_to_bot("edit_message", chat_id, text, message_id=message_id)
        game_info_delete(room_number, "game_phase")
        game_info_add(room_number, "game_phase", "lady_start")
        set_room_timer(5, room_number)
    elif game_phase == "lady_start":
        lady = check_certain_game_info(room_number, "lady")
        if lady == "disabled":
            game_info_delete(room_number, "game_phase")
            game_info_add(room_number, "game_phase", "night_result")
            phase_dispatcher(room_number)
            return None
        elif "died" in lady:
            refresh_all_keyboards_in_room(room_number, "Прокидається леді і вибирає свого обранця на ніч...", admin_exception=False)
        else:
            refresh_all_keyboards_in_room(room_number, "Прокидається леді і вибирає свого обранця на ніч...", admin_exception=False, subgroup_exception="lady", subgroup_text="Виберіть свого обранця на ніч:")
        game_info_delete(room_number, "game_phase")
        game_info_add(room_number, "game_phase", "lady_end")
        set_room_timer(25, room_number)
    elif game_phase == "lady_end":
        lady = check_certain_game_info(room_number, "lady")
        people = check_certain_game_info(room_number, "people").strip(';').split(';')
        if not check_night_action(room_number, "lady"):
            if lady != "disabled" and "died" not in lady:
                print('Зашло')
                people.remove(lady)
                selected_person = choice(people)
                moniker = check_certain_user_info(selected_person, "moniker")
                activity = "edit_message"
                text = f"Ви надаете алібі {moniker}"
                night_number = check_day_number(room_number)
                game_info_add(room_number, f"night_{night_number}", "l|" + selected_person + '|')
                chat_id = check_certain_user_info(lady, "chat_id")
                message_id = check_keyboard_message_id(room_number, lady, chat_id=chat_id)
                ask_to_bot(activity, chat_id, text, message_id=message_id)
        game_info_delete(room_number, "game_phase")
        game_info_add(room_number, "game_phase", "night_result")
        set_room_timer(5, room_number)
    elif game_phase == "night_result":
        mafia_result, mafia_selected_count = check_night_action_result(room_number, "mafia")
        sheriff = check_certain_game_info(room_number, "sheriff")
        doctor = check_certain_game_info(room_number, "doctor")
        lady = check_certain_game_info(room_number, "lady")
        sheriff_result, doctor_result = "", ""
        if sheriff != "disabled":
            sheriff_choice, sheriff_result = check_night_action_result(room_number, "sheriff")
        if doctor != "disabled":
            doctor_choice, doctor_result = check_night_action_result(room_number, "doctor")
        if lady != "disabled":
            lady, nothing = check_night_action_result(room_number, "lady")
        moniker_result = check_certain_user_info(mafia_result, "moniker")
        text = "Місто прокидається з такими новинами:\n"
        if doctor != "disabled":
            if doctor_result == "Yes":
                text += "Доктор зміг вилікувати жертву мафії\n"
            else:
                text += f"Мафія цієї ночі вбила {moniker_result}, на жаль доктор не встиг його врятувати\n"
                make_spectator(room_number, mafia_result)
        else:
            text += f"Мафія цієї ночі вбила {moniker_result}\n"
            make_spectator(room_number, mafia_result)
        if sheriff != "disabled":
            if sheriff_result == "Yes":
                text += "Шериф цієї ночі дізнався про належність однієї людини до мафії\n"
            else:
                text += "Шериф цієї ночі довів невиність однієї людини\n"
        if lady != "disabled":
            text += "Леді сьогодна провела гарну ніч\n"
        night_result, who_win = is_game_over(room_number)
        if night_result:
            game_info_delete(room_number, "game_phase")
            game_info_add(room_number, "game_phase", "game_over")
        else:
            game_info_delete(room_number, "game_phase")
            game_info_add(room_number, "game_phase", "election_start")
        phase_dispatcher(room_number, previous_text=text)
    elif game_phase == "game_over":
        nothing, winners = is_game_over(room_number)
        previous_text += "Гру завершенно, " + ("перемогла мафія" if winners == "mafia" else "перемогли мирні жителі") + "!!!"
        refresh_all_keyboards_in_room(room_number, previous_text, admin_exception=False)
        people = check_certain_game_info(room_number, "people").strip(';').split(';')
        for person in people:
            change_certain_user_info(person, "in_room", "False")
            chat_id = check_certain_user_info(person, "chat_id")
            ask_to_bot("send_message", chat_id, "Давай зіграємо ще одну гру!", markup=turn_on_menu_butons())
        exempt_room(room_number)

def in_game_calldata_analysing(message_id, user_id, chat_id, calldata_text):
    activity = "ignore"
    text = ""
    markup = None
    user_id = str(user_id)
    if calldata_text[:2] == "G1":
        selected_person, room_number = calldata_text[3:].split('/')
        activity = "edit_message"
        moniker = ""
        if selected_person != "skip":
            moniker = check_certain_user_info(selected_person, "moniker")
        text = f"Ви відали свій голос за {moniker}" if selected_person != 'skip' else f"Ви відали свій голос за пропуск голосування"
        day_number = check_day_number(room_number)
        game_info_add(room_number, f"day_{day_number}", selected_person + '/' + user_id + ';')
    elif calldata_text[:2] == "G2":
        selected_person, room_number = calldata_text[3:].split('/')
        activity = "edit_message"
        moniker = check_certain_user_info(selected_person, "moniker")
        text = f"Ви хочите вбити {moniker}"
        night_number = check_day_number(room_number)
        game_info_add(room_number, f"night_{night_number}", selected_person + '/' + user_id + ';')
    elif calldata_text[:2] == "G3":
        selected_person, room_number = calldata_text[3:].split('/')
        activity = "edit_message"
        mafia = check_certain_game_info(room_number, "mafia").strip(';').split(';')
        is_mafia = True if selected_person in mafia else False
        moniker = check_certain_user_info(selected_person, "moniker")
        text = f"Ви перевіряете {moniker}\nРезультат: " + "Він є членом мафії" if is_mafia else "Він не є мафією"
        night_number = check_day_number(room_number)
        game_info_add(room_number, f"night_{night_number}", "s|" + selected_person + '/' + ("Yes" if is_mafia else "No") + '|')
    elif calldata_text[:2] == "G4":
        selected_person, room_number = calldata_text[3:].split('/')
        activity = "edit_message"
        mafia_choice, selected_mafia_count = check_night_action_result(room_number, "mafia")
        is_heal = True if selected_person == mafia_choice else False
        moniker = check_certain_user_info(selected_person, "moniker")
        text = f"Ви надаете медичну допомогу {moniker}\nРезультат: " + "Ви вилікували жертву мафії" if is_heal else "Ви не вилікували жертву мафії"
        night_number = check_day_number(room_number)
        game_info_add(room_number, f"night_{night_number}", "d|" + selected_person + '/' + ("Yes" if is_heal else "No") + '|')
    elif calldata_text[:2] == "G5":
        selected_person, room_number = calldata_text[3:].split('/')
        activity = "edit_message"
        moniker = check_certain_user_info(selected_person, "moniker")
        text = f"Ви надаете алібі {moniker}"
        night_number = check_day_number(room_number)
        game_info_add(room_number, f"night_{night_number}", "l|" + selected_person + '|')
    return activity, text, markup

def stop_game(room_number, text_to_users = 'Гру закінчео!\nСподіваємося, що вам все сподобалося'):
    people = check_certain_game_info(room_number, "people").strip().strip(';').split(';')
    for person in people:
        person_leave(room_number, person, text_instead_keyboard=text_to_users)
    game_info_delete(room_number, "game_phase")
    game_info_add(room_number, "game_phase", "stopped")
    exempt_room(room_number)

def set_room_timer(time_in_seconds, room_number):
    new_timer = Timer(time_in_seconds, time_over(room_number))
    new_timer.start()

def time_over(room_number):
    def link_to_function():
        return phase_dispatcher(room_number)
    return link_to_function

def start_game(room_number):
    people = check_certain_game_info(room_number, "people").strip(';').split(';')
    if len(people) < 4:
        return False
    elif len(people) > 17:
        return False
    game_info_delete(room_number, "game_phase")
    game_info_add(room_number, "game_phase", "role_giving")
    refresh_all_keyboards_in_room(room_number, "Початок гри", admin_exception=False)
    phase_dispatcher(room_number)
    return True, ""

def make_missed_votes(room_number, day_phase, day_number, votes, subgroup = "people"):
    people = check_certain_game_info(room_number, subgroup).strip(';').split(';')
    not_in_subgroup = people
    if subgroup != "people":
        not_in_subgroup = check_certain_game_info(room_number, "people").strip(';').split(';')
        for person in not_in_subgroup:
            if person in people:
                not_in_subgroup.remove(person)
    try:
        voted_users = [voted_user_id[(voted_user_id.find('/') + 1):] for voted_user_id in votes]
    except ValueError:
        voted_users = []
    for person in people:
        if person not in voted_users:
            selected_person = choice(not_in_subgroup)
            game_info_add(room_number, f"{day_phase}_{day_number}", selected_person + '/' + person + ';')
            votes.append(selected_person + '/' + person)
    return votes

def check_night_action(room_number, role = "", night_number=None):
    conclusion = None
    if night_number == None:
        night_number = check_day_number(room_number)
    night_events = check_certain_game_info(room_number, f"night_{night_number}")
    if role == "sheriff":
        conclusion = False
        if "|s|" in night_events:
            conclusion = True
        else:
            conclusion = False
    elif role == "doctor":
        if "|d|" in night_events:
            conclusion = True
        else:
            conclusion = False
    elif role == "lady":
        if "|l|" in night_events:
            conclusion = True
        else:
            conclusion = False
    return conclusion

def check_night_action_result(room_number, role = "", previous_day=False):
    result = ""
    additional_info = ""
    night_number = check_day_number(room_number)
    if previous_day:
        night_number = str(int(night_number) - 1)
    night_events = check_certain_game_info(room_number, f"night_{night_number}")
    if role == "mafia":
        mafia_action = night_events[:night_events.find('|')]
        result, additional_info = mafia_action[(mafia_action.find('-') + 1):].split('/')
    else:
        role_info = check_night_action(room_number, role, night_number=night_number)
        if role_info:
            night_events = night_events[(night_events.find(f"|{role[0]}|") + 3):]
            role_action = night_events[:night_events.find('|')]
            if '/' in role_action:
                result, additional_info = role_action.split('/')
            else:
                result = role_action
        else:
            result = "died"
    return result, additional_info

def is_game_over(room_number):
    people = check_certain_game_info(room_number, "people").strip(';').split(';')
    mafia = check_certain_game_info(room_number, "mafia").strip(';').split(';')
    if mafia == [""]:
        return True, "civilians"
    elif len(people) - len(mafia) <= len(mafia):
        return True, "mafia"
    else:
        return False, ""
