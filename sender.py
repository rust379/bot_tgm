"""
Api for send message from bot.BOT
"""
import bot


def send_message(chat_id, message):
    """Send message.
    Now it can send:
        text
    In future plans:
        message with buttons,
        pictures

    Args:
        chat_id: bot chat id
        message: text for sending
    """
    bot.BOT.send_message(chat_id, message)
