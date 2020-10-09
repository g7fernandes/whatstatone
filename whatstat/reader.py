from typing import TextIO, List, Dict
from datetime import datetime
import re
from utils import remove_control_chars, log2console, date2int


repeated_names_map: Dict[str, str] = {}


def get_time(words: List[str]):
    # in some languages the backup is written with
    # dd/mm/yyyy hh:mm -
    # and others add some word:
    # dd/mm/yyyy at hh:mm -
    # we need to check for the '-', it will be in the 3rd or 4th position
    # TODO: Unhardcode the position of '-', use the file to check the
    # probable position
    if words[2] == '-':
        time = words[1].split(':')
    elif words[3] == '-':
        time = words[2].split(':')
    else:
        return None
    if len(time) == 2:
        return (int(time[0]), int(time[1]))
    return None


def get_datetime(words: List[str]):
    if len(words) < 4 or words[3][0:1] == '\u200e':
        return None
    date = [int(num) for num in re.split(r'/|\.|,', words[0]) if num.isdigit()]
    if len(date) != 3:
        return None
    elif date[2] < 2009:
        date[2] += 2000

    if time := get_time(words):
        return datetime(date[2], date[1], date[0], time[0], time[1])


def get_name(line: str) -> str:
    name = re.search(r'- (.*?):', remove_control_chars(line))
    if name and not name.group(1).isspace():
        return name.group(1)
    return ''


class Message:
    # date of the first Message in people dict
    initial_date: datetime = datetime(1970, 1, 1)
    # date of the last Message people dict
    final_date: datetime = datetime(1970, 1, 1)

    def __init__(self, line: str, date: datetime):
        self.date = self.set_final_date(self.set_initial_date(date))
        # removes the time and sender label
        self.lines = [line.split(':', 2)[2]]

    def append_msg(self, line: str):
        self.lines.append(line)

    def get_number_of_words(self):
        number = 0
        for line in self.lines:
            number += len(line)
        return number

    @classmethod
    def set_initial_date(cls, date: datetime) -> datetime:
        if cls.initial_date == datetime(1970, 1, 1) or cls.initial_date > date:
            cls.initial_date = date
            return date
        else:
            return date

    @classmethod
    def set_final_date(cls, date: datetime) -> datetime:
        if not cls.final_date or cls.final_date < date:
            cls.final_date = date
        return date


def add_new_Message(people: Dict, text: str, sender: str, time: datetime):
    # TODO: validation
    if not sender:
        return
    if sender in people:
        if people[sender].get(date2int(time)):
            people[sender][date2int(time)].append(Message(text, time))
        else:
            people[sender][date2int(time)] = [Message(text, time)]
    else:
        people[sender] = {date2int(time): [Message(text, time)]}


def check_most_similar(new_name: str, candidates: List[str]):
    if len(candidates) == 1:
        return candidates[0]
    splitted_new_name = new_name.split()

    pontuation = []
    for candidate in candidates:
        pts = 0
        inew = 0
        for new in splitted_new_name:
            icand = 0
            for cand in candidate.split():
                if new in cand:
                    pts += 1
                if cand in new:
                    pts += 1
                if pts == 2 and icand == inew:
                    pts += 1
                icand += 1
            inew += 1
        pontuation.append(pts)
    return candidates[pontuation.index(max(pontuation))]


def detect_similar_names(
    people: Dict[str, Dict[int, List[Message]]],
    new_name: str,
    merge: bool
) -> str:
    if not new_name or new_name in people:
        return new_name  # type: ignore
    if new_name in repeated_names_map:
        return repeated_names_map[new_name]
    candidates: List[str] = []
    for name in people.keys():
        if new_name in name or name in new_name:
            candidates.append(name)

    if candidates:
        name = check_most_similar(new_name, candidates)
        log2console('\x1b[0;30;43mProbably the same person:'
                    f'"{name}" and "{new_name}". \x1b[0m')
        if merge:
            repeated_names_map[new_name] = name
            log2console('\x1b[0;30;43mMerging.\x1b[0m\n')
            return name
        else:
            log2console('\x1b[0;30;43mMerging.Not merging.\x1b[0m\n')
            return new_name
    return new_name


def leitor(file: TextIO,
           merge_similar_names: bool) -> Dict[str, Dict[int, List[Message]]]:
    sender = ''
    people: Dict[str, Dict[int, List[Message]]] = {}

    for line in file:
        # clean problematic character
        if date := get_datetime(line.split()):
            date_current = date
            sender = detect_similar_names(people,
                                          get_name(line),
                                          merge_similar_names)
            add_new_Message(people, line, sender, date_current)
        elif sender:
            people[sender][date2int(date_current)][-1].append_msg(line)
    return people
