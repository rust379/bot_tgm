"""
    General purpose functions
"""
import time
from datetime import datetime
import re


def check_date_correct(date):
    """
    Check date for correctness
    Correct formats: 'dd.mm'(+'.yy') (+'hh.mm') or 'hh.mm'
    :param str date: Checking date
    :return bool: True if date is correct
            str: text of error
    """
    if not (re.fullmatch(r"\d\d.\d\d(.\d\d)?( \d\d:\d\d)?", date) or
            re.fullmatch(r"\d\d:\d\d", date)):
        return False, "Неправильный формат даты"
    month = 0
    day = 0
    if date[-3] == ':':
        if date[-5:-3] > "23" or date[-2:] > "59":
            return False, "Некорректное время"
    if date[2] == '.':
        month = int(date[3:5])
        day = int(date[0:2])
        if month == 0 or day == 0 or month > 12:
            return False, "Некорректный день или месяц"
    year: int = datetime.now().year
    if len(date) > 7 and date[5] == '.':
        year = int(date[6:8])

    if month < datetime.now().month or (
            month == datetime.now().month and day < datetime.now().day):
        year += 1
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if year % 4 == 0:
        days_in_month[1] = 29
    if month and day > days_in_month[month - 1]:
        return False, "Некорректный день"
    return True, "Корректная дата"


def timestamp(date):
    """
    from str to timestamp
    :param str date: User's message
    :return int time_int: Time in timestamp
    """
    time_str = str(datetime.now())[0:16]
    if date[-3] != ':':
        date += " 00:00"
    day = False
    if date[2] == '.':
        if date[5] == '.':
            date = date[0:6] + time_str[0:2] + date[6:]
        else:
            date = date[0:5] + '.' + time_str[0:4] + date[5:]
        day = True
    else:
        date = time_str[8:10] + '.' + time_str[5:7] + '.' + time_str[0:4] + ' ' + date

    time_int = time.mktime(datetime.strptime(date, "%d.%m.%Y %H:%M").timetuple())
    if date[-5:] < time_str[-5:16] and not day:
        time_int += 60 * 60 * 24
    if time_int < time.time():
        date = date[0:6] + str(int(date[6:10]) + 1) + date[10:]
        time_int = time.mktime(datetime.strptime(date, "%d.%m.%Y %H:%M").timetuple())
    return time_int
