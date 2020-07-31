"""
    Classes for working with users notifications
"""
from enum import Enum


class NotificationPeriod(Enum):
    """
        Contains a list of available periods
    """
    NO_PERIOD = 0
    DAY = 24 * 60 * 60
    WEEK = 7 * 24 * 60 * 60
    TWO_WEEKS = 14 * 24 * 60 * 60


class Notification:
    """
    Class notification,
    contains methods for working with the notification object
    """

    def __init__(self,
                 chat_id: int = 0,
                 notification_id: int = 0,
                 title: str = "",
                 next_date: int = 0,
                 period: NotificationPeriod = NotificationPeriod.NO_PERIOD,
                 is_active: bool = True):
        """
        Initialize class

        :param integer chat_id: id user chat
        :param integer notification_id: number of user notification
        :param string title: notification title
        :param integer next_date: when should we send a notification next time
        :param NotificationPeriod period: optional, the period for sending the notification
        :param bool is_active: optional, is notification active
        """
        self.chat_id = chat_id
        self.notification_id = notification_id
        self.title = title
        self.next_notification_date = next_date
        self.period = period
        self.is_active = is_active

    def to_list(self):
        """
        notification to list
        :return list: list of notification fields
        """
        notification_list = [self.chat_id,
                             self.notification_id,
                             self.title,
                             self.next_notification_date,
                             self.period.value,
                             self.is_active]
        return notification_list

    def data_key(self):
        """
        get notification key fields
        :return list[str]: list of notification key fields
        """
        notification_list = ["chat_id = {}".format(self.chat_id),
                             "notification_id = {}".format(self.notification_id)]
        return notification_list

    def record_notif(self, database):
        """
        Record new notification to database
        :param database.Database database: database
        :return:
        """
        if not self.notification_id:
            self.notification_id = next_notification_id(database, self.chat_id)
        database.insert_into_table("user_notifications", self.to_list())


def next_notification_id(database, chat_id):
    """
    Get next notification id for user
    :param database.Database database: database
    :param integer chat_id: chat id
    :return integer: id for next notification
    """
    query = """
            SELECT notification_id
            FROM user_notification_id
            WHERE chat_id = {}
            """.format(chat_id)
    result = database.query(query)
    next_id = 1

    if result:
        next_id += result[0]["notification_id"]
    if next_id == 1:
        database.insert_into_table("user_notification_id", [chat_id, next_id])
    else:
        database.update_record("user_notification_id",
                               ["chat_id = {}".format(chat_id)],
                               "notification_id = {}".format(next_id))
    return next_id
