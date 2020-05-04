"""
Create telegram bot and define message_handlers for it
"""
import telebot
import botToken
import database as db
import cfCommands as cf


class BotRun(telebot.TeleBot):
    """Bot instance with connected database"""
    database: type(db.Database)

    def __init__(self, token):
        """Init telegram bot with token"""
        self.current_event = dict()

        super().__init__(token)

    def set_database(self, database):
        """Set database"""
        self.database = database

    def run(self):
        """Execute bot with none_stop=True"""
        self.polling(none_stop=True)


BOT = BotRun(botToken.token)


@BOT.message_handler(commands=["start"])
def welcome(message):
    """Send welcome text to chat id, which specified in message param"""
    message_text = ("Добро пожаловать, {0.first_name}!\n"
                    "Я - <b>{1.first_name}</b>, бот, "
                    "созданный чтобы быть подопытным кроликом.").format(
                        message.from_user, BOT.get_me())
    BOT.send_message(message.chat.id, message_text, parse_mode="html")


@BOT.message_handler(commands=["help"])
def commands_list(message):
    """Send list of commands to chat id, which specified in message param"""
    list_of_commands = ["/myRating"]
    commands_str = ""
    for command in list_of_commands:
        commands_str = commands_str + "\n" + command
    BOT.send_message(message.chat.id,
                     "Вот список моих команд:" + commands_str,
                     parse_mode="html")


@BOT.message_handler(commands=["register"])
def register(message):
    """Change current action to registartion for chat id"""
    BOT.send_message(message.chat.id,
                     "Пожалуйста, скажите нам ваш логин на codeforces")
    BOT.current_event[str(message.chat.id)] = "REGISTRATION"


@BOT.message_handler(commands=["myRating"])
def cur_user_rating(message):
    """Send info about current rating, if chat id was registered with cf_login"""
    params = db.get_request_struct()
    params["attributes"].append("cf_login")
    params["conditions"].append("chat_id = {}".format(message.chat.id))
    cf_login = BOT.database.data_from_table('users', params)
    if cf_login:
        message_text = cf.curUserRating(cf_login[0][0])
        BOT.send_message(message.chat.id, message_text, parse_mode="html")


@BOT.message_handler(content_types=["text"])
def text_message_handler(message):
    """Analyze user"s current event and performs an action based on it

    Possible values for event:
        "REGISTRATION" - register user codeforces login in database
    If nothing event provided - ignore message"""

    if BOT.current_event[str(message.chat.id)] == "REGISTRATION":
        BOT.database.insert_into_table(
            "users",
            [message.from_user.username, message.text, message.chat.id])
        BOT.current_event.pop(message.chat.id, None)
