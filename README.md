# MafiaBot
Telegram bot for playing Mafia in it.

I'd like to introduce my first project, MafiaBot, written in Python using the pyTelegramBotAPI library. The purpose of the bot is to facilitate playing the game "Mafia", but communication between players should be in voice chat in their private group on the messenger platform.

Files:

main.py: This is the main file and launch point for the bot. files_operations.py: This file contains all the functions that work with the database. While I wrote these functions myself, it would have been better to use libraries such as "pandas" for this purpose. However, I was not familiar with these libraries at the time of writing. function.py: This file contains a large portion of the bot's functions. game_processing.py: This file contains the functions that handle game processing. bot_processing.py: This file contains the functions that analyze all requests made to the bot. room_setup.py: This file serves as a connecting point between "bot_processing.py" and "game_processing.py," and also assists in analyzing requests. setup.py: This file is used solely for server installation. Please refer to the "Installation" section for more information.

Installation:

Simply launch the "setup.py" file and it will automatically create all necessary files for the bot. The file structure will be as follows:

Storage: 1.1) Rooms: 1.1.1) Files from "room1" to "room10" 1.1.2) rooms_concierge 1.2) users_files: (After installation, this folder will be empty, but it will contain all users' files, with one file per user). 1.3) Allowed_symbols (This file contains all the symbols that are allowed in a user's username in the bot.)
