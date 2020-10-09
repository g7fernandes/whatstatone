from typing import Dict, List, Tuple, TypeVar
from reader import Message
from datetime import datetime, timedelta
import numpy as np
from utils import date2int

T = TypeVar('T')
TriTuple = Tuple[T, T, T]


def info_per_hour_day(
    people: Dict[str, Dict[int, List[Message]]],
    is_msg_criteria: bool = True
) -> Dict[str, np.array]:
    '''
    info_per_hour_day
    -----------------

    Builds a dictionary containing calendars per person. The calendar
    is an array 24x<number_of_days> in which each element [n,m] represents
    the number of messages sent at time n and day m. The days are how many
    days passed since the first message was sent.

    '''

    if Message.final_date and Message.initial_date:
        final = datetime(Message.final_date.year,
                         Message.final_date.month,
                         Message.final_date.day)
        start = datetime(Message.initial_date.year,
                         Message.initial_date.month,
                         Message.initial_date.day)
        number_days = final - start
    info_per_person_day: Dict[str, np.array] = {}
    for person, messages in people.items():
        calendar: np.array = np.zeros((24, number_days.days + 1), dtype=int)
        for msg_list in messages.values():
            for msg in msg_list:
                if is_msg_criteria:
                    calendar[
                        msg.date.hour,
                        (datetime(msg.date.year, msg.date.month, msg.date.day)
                         - datetime(msg.initial_date.year,
                                    msg.initial_date.month,
                                    msg.initial_date.day)).days
                    ] += 1
                else:
                    calendar[
                        msg.date.hour,
                        (datetime(msg.date.year, msg.date.month, msg.date.day)
                         - datetime(msg.initial_date.year,
                                    msg.initial_date.month,
                                    msg.initial_date.day)).days
                    ] += len(''.join(msg.lines).split())

        info_per_person_day[person] = calendar
    return info_per_person_day


def who_sent_at_time(people: Dict[str, Dict[int, List[Message]]],
                     day: int,
                     hour: int,
                     silent_time: int) -> List[str]:

    actual_day = (datetime(year=Message.initial_date.year,
                           month=Message.initial_date.month,
                           day=Message.initial_date.day,
                           hour=hour)
                  + timedelta(days=day))
    # checks answers that hour
    senders: Dict[str, datetime] = {}
    for person, messages in people.items():
        t = 0
        while t <= silent_time and senders.get(person) is None:
            if (msgs_at_time := messages.get(
                    date2int(actual_day + timedelta(hours=t)))):
                senders[person] = msgs_at_time[0].date
            t += 1

    return [t[0] for t in sorted(senders.items(), key=lambda p: p[1])]


def conversation_starters(
    people: Dict[str, Dict[int, List[Message]]],
    calendar_array: Dict[str, np.array],
    silent_time: int
) -> TriTuple[List[Tuple[str, int]]]:
    '''
    conversation_starters
    ---------------------
    Returns who started conversation, who answared and who was ignored.
    The repliers didn't necessarily answared who sent first, but probably
    was induced to write a message when he or she saw the notification.

    Returns:
    -------
        (starters, repliers, ignored) : TriTuple[List[Tuple[str, int]]]
        The dictionare contains the name of the person and how many times
        s/he induced conversation, replied or was ignored.

    '''
    final = datetime(Message.final_date.year,
                     Message.final_date.month,
                     Message.final_date.day)
    start = datetime(Message.initial_date.year,
                     Message.initial_date.month,
                     Message.initial_date.day)
    ndays = (final - start).days + 1
    all_info: np.array = np.zeros((24, ndays), dtype=int)
    for name, info in calendar_array.items():
        all_info += info

    time_since_last_message = 0

    starters: Dict[str, int] = {}
    repliers: Dict[str, int] = {}
    ignored: Dict[str, int] = {}

    # TODO: try a vectorized approach
    for day in range(ndays):
        for hour in range(24):
            if all_info[hour, day] and time_since_last_message >= silent_time:
                senders = who_sent_at_time(people, day, hour, silent_time)
                if len(senders) == 1:
                    if ignored.get(senders[0]):
                        ignored[senders[0]] += 1
                    else:
                        ignored[senders[0]] = 1
                else:
                    if starters.get(senders[0]):
                        starters[senders[0]] += 1
                    else:
                        starters[senders[0]] = 1
                    if repliers.get(senders[1]):
                        repliers[senders[1]] += 1
                    else:
                        repliers[senders[1]] = 1

                time_since_last_message = 0
            else:
                time_since_last_message += 1

    return (
        sorted(starters.items(), reverse=True, key=lambda kv: kv[1]),
        sorted(repliers.items(), reverse=True, key=lambda kv: kv[1]),
        sorted(ignored.items(), reverse=True, key=lambda kv: kv[1])
    )
