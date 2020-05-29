"""
Execute and control all threads
"""
import threading
import database
import bot
import cf_daemon as cf

DATABASE = database.Database()
DATABASE.create_table("users",
                      ["`chat_id` INT UNSIGNED PRIMARY KEY NOT NULL",
                       "`tgm_name` VARCHAR(100) NULL",
                       "`cf_handle` VARCHAR(100) NULL"])
DATABASE.create_table("cf_notifications",
                      ["`cf_handle` VARCHAR(100) PRIMARY KEY NOT NULL",
                       "`contest_notification` BOOL NULL"])

bot.BOT.set_database(DATABASE)
BOT_THREAD = threading.Thread(target=bot.BOT.run)

CF_DAEMON = cf.CodeforcesDaemon(DATABASE)
CF_THREAD = threading.Thread(target=CF_DAEMON.run, daemon=True)

CF_THREAD.start()

BOT_THREAD.start()
BOT_THREAD.join()
