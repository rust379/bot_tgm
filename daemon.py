"""
Execute and control all threads
"""
import threading
import database
import bot
import cf_daemon as cf

DATABASE = database.Database()
DATABASE.create_table("users", ["tgm_name", "cf_handle", "chat_id"])
DATABASE.create_table("cf_notifications",
                      ["cf_handle", "contest_notification"])

bot.BOT.set_database(DATABASE)
BOT_THREAD = threading.Thread(target=bot.BOT.run)

CF_DAEMON = cf.CodeforcesDaemon(DATABASE)
CF_THREAD = threading.Thread(target=CF_DAEMON.run, daemon=True)

CF_THREAD.start()
BOT_THREAD.start()
BOT_THREAD.join()
