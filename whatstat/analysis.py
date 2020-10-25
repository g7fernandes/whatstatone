from reader import Message, fit_dates_to_history_time_length
from typing import List, Dict, Tuple
from datetime import datetime
import numpy as np
from utils import get_different_key


def rank_group_conversation(
    init_date: datetime,
    final_date: datetime,
    cumulative_calendar_dict: Dict[str, np.array]
) -> Dict[str, np.array]:
    rank: Dict[str, int] = {}

    if Message.initial_date > init_date:
        init_date = Message.initial_date
    if Message.final_date < final_date:
        final_date = Message.final_date
    start = (init_date - Message.initial_date).days
    final = (final_date - Message.initial_date).days

    for person, cumulative_calendar in cumulative_calendar_dict.items():
        rank[person] = cumulative_calendar[final] - cumulative_calendar[start]
    return dict(sorted(rank.items(), key=lambda kv: kv[1], reverse=True))


def rank_private_conversations(
    init_date: datetime,
    final_date: datetime,
    cumulative_calendar_dict_list: List[Dict[str, np.array]],
    criteria: str,
    my_names: List[str]
) -> List[Tuple[str, int]]:
    '''
    Input:
        init_date : datetime
            Initial date consider
        final_date : datetime
            Final date to consider
        cumulative_calendar_dict_list : Dict[str, np.array]
            Dictionary with the cumulative number of messages sent per person.
        criteria : str
            Options are 'sent', 'received' and 'exchanged'.
        my_names : List[str]
            Name(s) of the owner of the history. The criteria will use set
            or received relative to the the owner. Is a list to handle the
            case where the name of the sender changed over the history.
    '''
    rank: Dict[str, int] = {}
    rank_of_conversation: Dict[str, int] = {}

    (start, final) = fit_dates_to_history_time_length(init_date, final_date)

    for cumulative_calendar_dict in cumulative_calendar_dict_list:
        other = ''
        for person, cumulative_calendar in cumulative_calendar_dict.items():
            rank_of_conversation[person] = (cumulative_calendar[final]
                                            - cumulative_calendar[start])
            other = person if person not in my_names else other
        if criteria == 'exchanged':
            rank[other] = sum(rank_of_conversation.values())
        elif criteria == 'sent':
            for name in my_names:
                rank[other] = rank_of_conversation.get(name, 0)
        else:
            rank[other] = rank_of_conversation[other]

    return sorted(rank.items(), key=lambda kv: kv[1])


def cumulative_calendar(info_per_person_day: Dict[str, np.array]
                        ) -> Dict[str, np.array]:
    cumulative_info: Dict[str, np.array] = {}
    for person, calendar in info_per_person_day.items():
        cumulative_info[person] = np.cumsum(np.sum(calendar, axis=0))
    return cumulative_info


def get_moving_average(
    window: int,
    cumulative_info: Dict[str, np.array]
) -> Dict[str, np.array]:
    moving_average: Dict[str, np.array] = {}

    for person, info in cumulative_info.items():
        moving_average[person] = (info[window:] - info[:-window]) / window
        if 'TOTAL' in moving_average:
            moving_average['TOTAL'] += moving_average[person]
        else:
            moving_average['TOTAL'] = np.copy(moving_average[person])

    return moving_average


def join_calendars(calendar_list: List[Dict[str, np.array]],
                   by_me: str,
                   my_names: List[str]) -> Dict[str, np.array]:

    if len(calendar_list) == 1:
        return calendar_list[0]

    joint_calendar: Dict[str, np.array] = {}
    for calendar in calendar_list:
        if by_me == 'received':
            others = get_different_key(my_names, calendar.keys())
            for oth in others:
                joint_calendar[others[0]] = calendar.get(oth)

        for name in my_names:
            if calendar.get(name) is not None:
                joint_calendar[my_names[0]] = calendar.get(name)
        if by_me == 'exchanged':
            for person in calendar.keys():
                if person not in my_names:
                    joint_calendar[person] = (calendar[person]
                                              + calendar[my_names[0]])
    return joint_calendar


def get_mean_by_hour(
    info_per_person_day: Dict[str, np.array]
) -> Dict[str, np.array]:
    hourly: Dict[str, np.array] = {}
    total = np.zeros(24)
    for name, data in info_per_person_day.items():
        hourly[name] = np.mean(data, axis=1)
        total += hourly[name]
    hourly['TOTAL'] = total
    return hourly


def get_mean_by_week(
    info_per_person_day: Dict[str, np.array]
) -> Dict[str, np.array]:
    only_days: Dict[str, np.array] = {}
    for name, calendar in info_per_person_day.items():
        only_days[name] = np.sum(calendar, axis=0)
    weekly: Dict[str, np.array] = {}
    total = np.zeros(7)
    for name, data in only_days.items():
        n_weeks = int(len(data) / 7)
        week_data = np.zeros(7)
        for week_num in range(n_weeks):
            week_data += data[week_num * 7:week_num * 7 + 7]
        weekly[name] = week_data / n_weeks
        total += week_data / n_weeks
    weekly['TOTAL'] = total
    # organize days. Monday = 0
    first_day = Message.initial_date.weekday()
    for name in weekly.keys():
        weekly[name] = np.roll(weekly[name], first_day)

    return weekly


def information_distribution_per_person(
    ranks: List[Dict[str, np.array]]
) -> np.array:

    if len(ranks) == 1:
        distribution = np.zeros((len(ranks[0]), 2))
        for i, v in enumerate(ranks[0].values()):
            distribution[i, 1] = v[-1]
            distribution[i, 0] = i + 1
        distribution[:, 1] = (np.cumsum(distribution[:, 1])
                              / np.sum(distribution[:, 1]))
        distribution[:, 0] /= len(ranks[0])
    else:
        distribution = np.zeros((len(ranks), 2))
        for i, rank in enumerate(ranks):
            converation_total = 0
            for v in rank.values():
                converation_total += v[-1]
            distribution[i, 1] = converation_total
            distribution[i, 0] = i + 1
        distribution[:, 1] = (np.cumsum(distribution[:, 1])
                              / np.sum(distribution[:, 1]))
        distribution[:, 0] /= len(ranks[0])
        pass
    return distribution
