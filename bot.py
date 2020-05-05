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
        """Init telegram bot with token.

        Args:
            token: string with telegram bot token
        """
        self.current_event = dict()

        super().__init__(token)

    def set_database(self, database):
        """Set database for further use

        Args:
            database: database.Database() class
        """
        self.database = database

    def run(self):
        """Execute bot with none_stop=True"""

        self.polling(none_stop=True)


BOT = BotRun(botToken.token)


@BOT.message_handler(commands=["start"])
def welcome(message):
    """Send welcome text to chat id, which specified in message param
    Create record in users table
    """

    message_text = ("Добро пожаловать, {0.first_name}!\n"
                    "Я - <b>{1.first_name}</b>, бот, "
                    "созданный чтобы быть подопытным кроликом.").format(
                        message.from_user, BOT.get_me())
    BOT.send_message(message.chat.id, message_text, parse_mode="html")

    BOT.database.insert_into_table(
        "users", [message.from_user.username, None, message.chat.id])


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


@BOT.message_handler(commands=["registerCfHandle"])
def register_cf_handle(message):
    """Change current action to registartion for chat id"""

    BOT.send_message(message.chat.id,
                     "Пожалуйста, скажите нам ваш логин на codeforces")
    BOT.current_event[str(message.chat.id)] = "CF_REGISTRATION"


@BOT.message_handler(commands=['notifyContest'])
def notify_about_contest(message):
    """Set contest_notify flag in true for user"""

    params = db.get_request_struct()
    params["attributes"].append("cf_handle")
    params["conditions"].append("chat_id = {}".format(message.chat.id))
    cf_handle = BOT.database.data_from_table("users", params)
    if cf_handle and cf_handle[0][0] is not None:
        BOT.database.insert_into_table("cf_notifications",
                                       [cf_handle[0][0], "true"])


@BOT.message_handler(commands=["myRating"])
def cur_user_rating(message):
    """Send info about current rating, if chat id was registered with cf_handle"""

    params = db.get_request_struct()
    params["attributes"].append("cf_handle")
    params["conditions"].append("chat_id = {}".format(message.chat.id))
    cf_handle = BOT.database.data_from_table("users", params)
    if cf_handle:
        message_text = cf.curUserRating(cf_handle[0][0])
        BOT.send_message(message.chat.id, message_text, parse_mode="html")


@BOT.message_handler(content_types=["text"])
def text_message_handler(message):
    """Analyze user"s current event and performs an action based on it

    Possible values for event:
        "CF_REGISTRATION" - register user codeforces login in database
    If nothing event provided - ignore message"""

    if str(message.chat.id) not in BOT.current_event.keys():
        return

    if BOT.current_event[str(message.chat.id)] == "CF_REGISTRATION":
        BOT.database.update_record("users", [
            'tgm_name = "{}" AND chat_id = {}'.format(
                message.from_user.username, message.chat.id)
        ], 'cf_handle = "{}"'.format(message.text))
        BOT.current_event.pop(message.chat.id, None)
