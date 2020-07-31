"""
    Class for online monitoring users notifications
"""

import time
import database as db
import sender
import notifications as notif


class NotificationDaemon:
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
        self.last_update = 0
        self.update_notification_set()
        self.database.create_table("user_notification_id",
                                   ["`chat_id` INT UNSIGNED PRIMARY KEY NOT NULL",
                                    "`notification_id` INT UNSIGNED NOT NULL"])

    def update_notification_set(self):
        """
        Loads notifications from the database and puts them in the class structure
        """
        now = int(time.time())

        params = db.get_request_struct()
        params["conditions"] = ("is_active = True",
                                "next_notification_date > {}".format(self.last_update),
                                "next_notification_date <= {}".format(now))
        notification_list = self.database.data_from_table("user_notifications", params)
        self.last_update = now
        self.notifications.clear()
        for cur_notification in notification_list:
            self.notifications.add(notif.Notification(cur_notification["chat_id"],
                                                      cur_notification["notification_id"],
                                                      cur_notification["title"],
                                                      cur_notification["next_notification_date"],
                                                      notif.by_value(cur_notification["period"]),
                                                      cur_notification["is_active"]))

    def run(self):
        """
        Execute notifications daemon:
        processing notifications from the database
        """
        while True:
            self.update_notification_set()
            for cur_notif in self.notifications:
                sender.send_message(cur_notif.chat_id, cur_notif.title)
                if cur_notif.period == notif.NotificationPeriod.NO_PERIOD:
                    self.database.remove_from_table("user_notifications",
                                                    cur_notif.data_key())
                else:
                    next_date = cur_notif.next_notification_date + cur_notif.period
                    new_value = "next_notification_date = {}".format(next_date)
                    self.database.update_record("user_notifications",
                                                cur_notif.data_key(),
                                                new_value)
            time.sleep(60)