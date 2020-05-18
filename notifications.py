"""
    Class for working with users notifications
    Class for online monitoring users notifications
"""
from enum import Enum
import time
import database as db
import sender


class NotificationPeriod(Enum):
    """
        Contains a list of available periods
    """
    no_period = 0
    day = 24 * 60 * 60
    week = 7 * 24 * 60 * 60
    two_weeks = 14 * 24 * 60 * 60


class Notification():
    """
    Class notification,
    contains methods for working with the notification object
    """
    def __init__(self,
                 chat_id,
                 notification_id,
                 title,
                 next_date,
                 period: NotificationPeriod = NotificationPeriod.no_period,
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
        Сonverts a notification to a list
        :return list: list of notification fields
        """
        notification_list = [self.chat_id,
                             self.notification_id,
                             self.title,
                             self.next_notification_date,
                             self.period,
                             self.is_active]
        return notification_list

    def data_key(self):
        """
        Сonverts a notification to a dictionary
        :return list: list of notification fields
        """
        notification_dict = {"chat_id" : self.chat_id,
                             "notification_id" : self.notification_id}
        return notification_dict

class NotificationDaemon():
    """
    Class for online monitoring users notifications
    """
    def __init__(self, database):
        """
        Initialize class

        :param database.Database database: database
        """
        self.database = database
        self.notifications = set()
        self.last_update = time.ctime(0)
        self.next_update = time.time()
        self.update_notification_set()

    def update_notification_set(self):
        """
        Loads notifications from the database and puts them in the class structure
        """
        now = time.time()
        self.last_update = now
        params = db.get_request_struct()
        params["conditions"] = ("is_active = True",
                                "next_notification_date > {}".format(self.last_update),
                                "next_notification_date <= {}".format(now))
        notification_list = self.database.data_from_table("user_notifications", params)

        for cur_notification in notification_list:
            self.notifications.add(Notification(cur_notification[0],
                                                cur_notification[1],
                                                cur_notification[2],
                                                cur_notification[3],
                                                cur_notification[4],
                                                cur_notification[5]))

    def run(self):
        """
        Execute notifications daemon:
        processing notifications from the database
        """
        while True:
            self.update_notification_set()
            for cur_notif in self.notifications:
                sender.send_message(cur_notif.chat_id, cur_notif.title)
                if cur_notif.period == NotificationPeriod.no_period:
                    self.database.remove_from_table("user_notifications",
                                                    cur_notif.data_key())
                else:
                    next_date = cur_notif.next_notification_date + cur_notif.period
                    new_value = "next_notification_date = {}".format(next_date)
                    self.database.update_record("user_notifications",
                                                cur_notif.data_key(),
                                                new_value)

def next_notification_id(database, chat_id):
    """
    Get next notification id for user
    :param integer chat_id: chat id
    :return integer: id for new notification
    """
    query = """
            SELECT MAX(notification_id) as max_id
            FROM user_notifications
            WHERE chat_id = {}
            """.format(chat_id)
    result = database.query(query)
    return result[0].max_id + 1
