"""
Execute and control all threads
"""
import threading
import database
import bot

DATABASE = database.Database()
DATABASE.create_table('users', ['tgm_name', 'cf_login', 'chat_id'])

bot.BOT.set_database(DATABASE)
BOT_THREAD = threading.Thread(target=bot.BOT.run)

BOT_THREAD.start()
BOT_THREAD.join()
