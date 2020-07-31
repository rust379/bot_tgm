"""
Execute and control all threads
"""
import threading
import database
import bot
import cf_daemon as cf
import notification_daemon

DATABASE = database.Database()
DATABASE.create_table("users",
                      ["`chat_id` INT UNSIGNED PRIMARY KEY NOT NULL",
                       "`tgm_name` VARCHAR(100) NULL",
                       "`cf_handle` VARCHAR(100) NULL"])
DATABASE.create_table("cf_notifications",
                      ["`cf_handle` VARCHAR(100) PRIMARY KEY NOT NULL",
                       "`contest_notification` BOOL NULL"])
DATABASE.create_table("user_notifications",
                      ["`chat_id` INT UNSIGNED NOT NULL",
                       "`notification_id` INT UNSIGNED NOT NULL",
                       "`title` MEDIUMTEXT NOT NULL",
                       "`next_notification_date` BIGINT NOT NULL",
                       "`period` INT UNSIGNED NULL",
                       "`is_active` BOOL NOT NULL",
                       "PRIMARY KEY (`chat_id`, `notification_id`)"])

bot.BOT.set_database(DATABASE)
BOT_THREAD = threading.Thread(target=bot.BOT.run)

CF_DAEMON = cf.CodeforcesDaemon(DATABASE)
CF_THREAD = threading.Thread(target=CF_DAEMON.run, daemon=True)

NOTIF_DAEMON = notification_daemon.NotificationDaemon(DATABASE)
NOTIF_THREAD = threading.Thread(target=NOTIF_DAEMON.run, daemon=True)

CF_THREAD.start()
NOTIF_THREAD.start()

BOT_THREAD.start()
BOT_THREAD.join()
