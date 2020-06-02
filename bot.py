"""
Create telegram bot and define message_handlers for it
"""
import telebot
import botToken
import database as db
import cfCommands as cf
import notifications as notif
import general_functions


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
    chat_id = message.chat.id
    BOT.send_message(chat_id, message_text, parse_mode="html")
    params = db.get_request_struct()
    params["conditions"] = ["chat_id = {}".format(chat_id)]
    if BOT.database.data_from_table("users", params):
        return
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


@BOT.message_handler(commands=["notifyContest"])
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


@BOT.message_handler(commands=["newNotif"])
def new_notification(message):
    """Creating a new notification"""
    message_text = "Пожалуйста, введите описание уведомления"
    chat_id = message.chat.id
    BOT.send_message(chat_id, message_text)
    BOT.current_event[str(chat_id)] = "NOTIF_GET_TITLE"
    BOT.current_data[str(chat_id)] = notif.Notification()


@BOT.message_handler(content_types=["text"])
def text_message_handler(message):
    """Analyze user"s current event and performs an action based on it
    Possible values for event:
        "CF_REGISTRATION" - register user codeforces login in database
    If nothing event provided - ignore message"""
    chat_id = message.chat.id
    if str(chat_id) not in BOT.current_event.keys():
        print(message)
        return

    if BOT.current_event[str(chat_id)] == "CF_REGISTRATION":
        BOT.database.update_record("users",
                                   ['chat_id = {}'.format(chat_id)],
                                   'cf_handle = "{}"'.format(message.text))
        BOT.current_event.pop(chat_id, None)
    elif BOT.current_event[str(chat_id)] == "NOTIF_GET_TITLE":
        BOT.current_data[str(chat_id)].title = message.text
        BOT.current_event[str(chat_id)] = "NOTIF_GET_TIME"
        message_text = "Введите дату и время в формате ДД.ММ.ГГ (или ДД.ММ) и/или ЧЧ:ММ"
        BOT.send_message(chat_id, message_text)
    elif BOT.current_event[str(chat_id)] == "NOTIF_GET_TIME":
        date = message.text
        correct, message_text = general_functions.check_date_correct(date)
        if correct:
            ts = general_functions.timestamp(date)
            if ts == -1:
                message_text = "Это время уже прошло"
            else:
                user_notif = BOT.current_data[str(chat_id)]
                user_notif.next_notification_date = ts
                user_notif.notification_id = notif.next_notification_id(BOT.database, chat_id)
                user_notif.chat_id = chat_id
                message_text = "Уведомление записано"
                BOT.current_event[str(chat_id)] = None
                BOT.database.insert_into_table("user_notifications",
                                               user_notif.to_list())
                print(user_notif.to_list())
        BOT.send_message(chat_id, message_text)
