import telebot
import random
import botToken
import cfCommands as cf
import database as db
 
from telebot import types

bot = telebot.TeleBot(botToken.token)
 
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id,
                     "Добро пожаловать, {0.first_name}!\nЯ - <b>{1.first_name}</b>, бот, созданный чтобы быть подопытным кроликом.".format(message.from_user, bot.get_me()),
                     parse_mode='html')

@bot.message_handler(commands=['help'])
def welcome(message):
    list_of_commands = ['/myRating'];
    commands_str = ""
    for command in list_of_commands:
        commands_str = commands_str + '\n' + command
    bot.send_message(message.chat.id,
                     "Вот список моих команд:" + commands_str,
                     parse_mode='html')

@bot.message_handler(commands=['myRating'])
def curUserRating(message):
    print(message.chat)
    print(bot)
    message_text = cf.curUserRating("rust");
    bot.send_message(message.chat.id, message_text, parse_mode = 'html')


# RUN
bot.polling(none_stop=True)


