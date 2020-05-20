"""
Execute and control all threads
"""
import threading
import database
import bot
import cf_daemon as cf
import notifications

DATABASE = database.Database()
DATABASE.create_table("users", ["tgm_name", "cf_handle", "chat_id"])
DATABASE.create_table("cf_notifications",
                      ["cf_handle", "contest_notification"])
DATABASE.create_table("user_notifications",
                      ["chat_id", "notification_id", "title", "next_notification_date", "period", "is_active"])

bot.BOT.set_database(DATABASE)
BOT_THREAD = threading.Thread(target=bot.BOT.run)

CF_DAEMON = cf.CodeforcesDaemon(DATABASE)
CF_THREAD = threading.Thread(target=CF_DAEMON.run, daemon=True)

NOTIF_DAEMON = notifications.NotificationDaemon(DATABASE)
NOTIF_THREAD = threading.Thread(target=NOTIF_DAEMON.run, daemon=True)

CF_THREAD.start()
NOTIF_THREAD.start()
BOT_THREAD.start()
BOT_THREAD.join()
