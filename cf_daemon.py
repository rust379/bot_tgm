"""
Class for online monitorinf for codeforces events
and support functions for it
"""
import datetime
from sortedcontainers import SortedSet
import codeforces as cf
import database as db
import sender


def add_to_dict(dictionary, key, value):
    """Add value to set dictionary[key]

    Args:
        dictionary: dict for adding value
        key: dict key
        value: value to add in dict[key] set
    """
    if key not in dictionary:
        dictionary[key] = SortedSet(
            key=lambda contest: (contest.start_time, contest.name))
    dictionary[key].add(value)


def get_remaining_time(event_timestamp):
    """Return string with human readable format of remaining time.

    Args:
        event_timestamp: integer; event start date in unix timestamp format
    """
    event_date = datetime.date.fromtimestamp(event_timestamp)
    current_date = datetime.date.today()

    if event_date == current_date:
        return "today in " + datetime.datetime.fromtimestamp(
            event_timestamp).strftime("%H:%M")
    if event_date == current_date + datetime.timedelta(days=1):
        return "tomorrow in " + datetime.datetime.fromtimestamp(
            event_timestamp).strftime("%H:%M")
    delta = (event_date - current_date)
    return "in {} days".format(delta.days)


def contest_from_database_record(record):
    """Create codeforces.Contest class from database record.

    Args:
        record: tuple; one database record
    Returns:
        contest: codeforces.Contest
    """
    contest = cf.Contest()
    contest.id = record[0]
    contest.name = record[1]
    contest.start_time = record[2]
    contest.phase = cf.ContestPhase[record[3]]
    return contest


class CodeforcesDaemon:
    """Class provides methods for tracking changes on codeforces.com"""
    def __init__(self, database):
        """Initialize class

        Args:
            database: database.Database
        """
        self.api = cf.CodeforcesAPI()
        self.timestamp2contests = {}
        self.contests = set()

        self.database = database
        self.load_contests_from_database()

    def __send_message(self, cf_handles, message_text):
        """Send message with message_text to each of cf_handles

        Args:
            cf_handles: list of tuples with codeforces handle. Ex. [(strizh78,), (rust,)]
            message_text: text for sending
        """
        for cf_handle in cf_handles:
            params = db.get_request_struct()
            params["attributes"].append("chat_id")
            params["conditions"].append('cf_handle = "{}"'.format(
                cf_handle[0]))
            chat_id = self.database.data_from_table("users", params)[0]
            sender.send_message(chat_id[0], message_text)

    def __create_contest_message(self, contests):
        """Form message text about contests and send it,
        if user has flag contest_notification = true.

        Args:
            contests: list of codeforces.Contest
        """
        message = "Hello!\n\n"
        for contest in contests:
            message += "{} will be start {}\n\n".format(
                contest.name, get_remaining_time(contest.start_time))

        params = db.get_request_struct()
        params["attributes"].append("cf_handle")
        params["conditions"].append('contest_notification = "true"')
        cf_handles = self.database.data_from_table("cf_notifications", params)
        self.__send_message(cf_handles, message)

    def load_contests_from_database(self):
        """Load contests from database to class structures.
        """
        self.database.create_table(
            "contests",
            ["contest_id", "contest_name", "start_timestamp", "phase"])
        db_contests = self.database.data_from_table("contests",
                                                    db.get_request_struct())
        for db_contest in db_contests:
            if db_contest[2] > int(datetime.datetime.now().timestamp()):
                contest = contest_from_database_record(db_contest)
                one_hour = 3600
                add_to_dict(self.timestamp2contests,
                            contest.start_time - one_hour, contest)
                add_to_dict(self.timestamp2contests,
                            contest.start_time - 24 * one_hour, contest)
                self.contests.add(contest.id)

    def update_contests_info(self, timestamp):
        """Update class structs and database records about contests..

        Args:
            timestamp: current timestamp
        """
        contests = self.api.contest_list()

        for contest in contests:
            if contest.start_time > timestamp and contest.id not in self.contests:

                self.database.insert_into_table("contests", [
                    contest.id, contest.name, contest.start_time,
                    contest.phase.value
                ])

                one_hour = 3600
                add_to_dict(self.timestamp2contests, timestamp, contest)
                add_to_dict(self.timestamp2contests,
                            contest.start_time - one_hour, contest)
                add_to_dict(self.timestamp2contests,
                            contest.start_time - 24 * one_hour, contest)
                self.contests.add(contest.id)

            elif contest.id in self.contests:
                if contest.start_time > timestamp:
                    self.database.update_record(
                        "contests", ["contest_id = {}".format(contest.id)],
                        'phase = "{}"'.format(contest.phase.value))
                else:
                    self.database.remove_from_table("contests",
                                                    {"contest_id": contest.id})
                    self.contests.remove(contest.id)


    def run(self):
        """Execute codeforces daemon:
            monitor codeforces and update information,
            monitor information and send messages, when it necessary.
        Current functional:
            monitor contests
        """
        while 1:
            try:
                current_timestamp = int(datetime.datetime.now().timestamp())

                if current_timestamp % 60 == 0:
                    self.update_contests_info(current_timestamp)
                if current_timestamp in self.timestamp2contests:
                    self.__create_contest_message(
                        self.timestamp2contests[current_timestamp])
            except Exception as error:
                print("Error in cf daemon:", error)
