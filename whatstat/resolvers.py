#!/usr/bin/env python3

from typing import Any, Dict, List, Tuple, Optional
from reader import Message, leitor
from collector import info_per_hour_day, conversation_starters, TriTuple
from analysis import (cumulative_calendar,
                      rank_private_conversations,
                      rank_group_conversation,
                      get_moving_average,
                      join_calendars,
                      get_mean_by_hour,
                      get_mean_by_week,
                      information_distribution_per_person)
from draw_graph import (draw_line_chart, draw_barchart,
                        animate, draw_hourly_mean,
                        draw_weekly_mean,
                        animate_better_barchart,
                        plot_zipf)
from utils import iso8601_to_datetime, get_different_key, log2console
import numpy as np
import os
import json
from datetime import timedelta
from matplotlib.pyplot import show
from datetime import datetime
import csv
import asyncio

# TODO maybe this could become GraphQL
# TODO to facilitate quering, all Branch classes could be derived from some
# query class
# v_ stands for 'value'


class graphBranch:
    def __init__(self, data, period, tasks, window=None):
        self._get_metadata(tasks)
        if 'line' in tasks['chart_type']:
            self.get_line_chart(data, period, window, tasks)
        if 'bar' in tasks['chart_type']:
            self.get_bar_chart(data, period, tasks)

    def _get_metadata(self, tasks):
        if isinstance(tasks['metadata'], str):
            with open(tasks['metadata']) as file_graph_metadata:
                self.graph_metadata = json.load(file_graph_metadata)
                if by_me := tasks.get('append_title'):
                    tasks['title'] = f'{tasks["title"]} {by_me}'

    def get_line_chart(self, datas, period, window, tasks):
        if window:
            draw_line_chart(
                datas.items(),
                period[0] + timedelta(days=window - 1),
                period[1],
                self.graph_metadata
            )
        else:
            draw_line_chart(
                datas.items(),
                period[0],
                period[1],
                self.graph_metadata
            )
        if tasks.get('animate'):
            self.get_animation(draw_line_chart, datas)

    def get_bar_chart(self, datas: Dict[str, np.array], period, tasks):
        data2graph = []
        if Message.initial_date > period[0]:
            period[0] = Message.initial_date
        if Message.final_date < period[1]:
            period[1] = Message.final_date
        start = (period[0] - Message.initial_date).days
        final = (period[1] - Message.initial_date).days

        for k, v in datas.items():
            data2graph.append((k, v[final] - v[start]))
        draw_barchart(
            sorted(data2graph, key=lambda kv: kv[1], reverse=True),
            self.graph_metadata
        )
        if tasks.get('animate'):
            self.get_animation(draw_barchart, datas)

    def get_animation(self, func, data):
        # TODO: implement animate line chart
        anim = self.graph_metadata['animation'].get(
            'use_bar_chart_race_package')
        if anim:
            animate_better_barchart(func, data, self.graph_metadata)
        elif anim is not None:
            animate(func, data, self.graph_metadata)
        else:
            print('Animate line chart not implemented.')


class moving_averageBranch:

    def __init__(self,
                 cumulative_arrays: List[Dict[str, np.array]],
                 period: List[datetime],
                 criteria: str,
                 tasks: Dict[str, Any]):
        self._get_moving_average_dicts(cumulative_arrays, criteria, tasks)
        self.get_graph(period, tasks)

    def _get_moving_average_dicts(self, cumulative_arrays, criteria, tasks):
        self.criteria = criteria
        self.window = tasks['window']
        if len(cumulative_arrays) > 1:
            self.moving_average = get_moving_average(
                tasks['window'],
                join_calendars(
                    cumulative_arrays,
                    tasks.get('sent_received_exchanged', 'exchanged'),
                    reader.my_name)
            )

        else:
            self.moving_average = get_moving_average(
                tasks['window'],
                cumulative_arrays[0]
            )

    def get_graph(self, period, tasks):
        if v_graph := tasks.get('graph'):
            self.graph = graphBranch(self.moving_average,
                                     period,
                                     v_graph,
                                     window=tasks['window'])

    def write(self):
        # this just saves the csv data
        n = 0

        fname = (f'Moving_average_{self.criteria}_'
                 f'{self.window}_days _{n}.csv')
        with open(
            os.path.join(
                reader.dirname,
                fname,
            ),
            'w'
        ) as f:

            writer = csv.writer(f)
            for k, v in self.moving_average.items():
                writer.writerow([k, *v])
        n += 0


class rankBranch:

    def __init__(self,
                 calendar_arrays: List[Dict[str, np.array]],
                 criteria: str,
                 tasks: Dict[str, Any]):
        self.group_rank: Optional[Dict[str, int]] = None
        self.private_ranks: Optional[Tuple[str, List[Tuple[str, int]]]] = None
        self.period: List[datetime]
        self.cumulative_arrays: List[Dict[str, np.array]]
        self._get_cumulative_arrays(calendar_arrays)
        self._get_period(tasks)
        self._get_group_rank()
        self._get_private_rank(tasks)
        self.get_moving_average(criteria, tasks)
        self.get_graph(tasks)
        self.information_distribution = information_distribution_per_person(
            self.cumulative_arrays
        )
        self.plot_zipf(criteria)

    def _get_cumulative_arrays(self,
                               calendar_arrays: List[Dict[str, np.array]]):
        self.cumulative_arrays = []
        for calendar_dict in calendar_arrays:
            self.cumulative_arrays.append(cumulative_calendar(calendar_dict))

    def _get_period(self, tasks: Dict[str, Any]) -> None:
        period = tasks['period']
        init_date = iso8601_to_datetime(period[0])
        final_date = iso8601_to_datetime(period[1])
        if Message.initial_date > init_date:
            init_date = Message.initial_date
        if Message.final_date < final_date:
            final_date = Message.final_date
        self.period = [init_date, final_date]

    def _get_group_rank(self) -> None:
        if len(self.cumulative_arrays) == 1:
            self.group_rank = rank_group_conversation(
                self.period[0],
                self.period[1],
                self.cumulative_arrays[0]
            )

    def _get_private_rank(self, tasks: Dict[str, Any]) -> None:
        if len(self.cumulative_arrays) < 2:
            return
        by_me = tasks.get('sent_received_exchanged')
        if not by_me:
            by_me = 'exchanged'
        self.private_ranks = (by_me, rank_private_conversations(
            self.period[0],
            self.period[1],
            self.cumulative_arrays,
            by_me,
            reader.my_name
        ))

    def get_graph(self, tasks: Dict[str, Any]) -> None:
        if v_graph := tasks.get('graph'):
            if len(self.cumulative_arrays) > 1:
                by_me = tasks.get('sent_received_exchanged')
                if not by_me:
                    by_me = 'exchanged'
                v_graph['append_criteria'] = by_me
                self.graphBranch = graphBranch(
                    join_calendars(self.cumulative_arrays,
                                   by_me,
                                   reader.my_name),
                    self.period,
                    v_graph
                )
            else:
                self.graphBranch = graphBranch(self.cumulative_arrays[0],
                                               self.period,
                                               v_graph)

    # TODO: move to graph branch

    def plot_zipf(self, criteria: str):
        plot_zipf(self.information_distribution, criteria)

    def get_moving_average(self,
                           criteria: str,
                           tasks: Dict[str, Any]) -> None:
        if v_tasks := tasks.get('moving_average'):
            self.moving_averageBranch = moving_averageBranch(
                self.cumulative_arrays,
                self.period,
                criteria,
                v_tasks
            )

    def write(self) -> str:
        out: List[str] = []
        i = 0
        v_prev = 0
        if self.group_rank:
            for k, v in self.group_rank.items():
                if v != v_prev:
                    i += 1
                    v_prev = v
                out.append(f'{i}. {k} - {v}\n')
        if self.private_ranks:
            out.append(f'\n{self.private_ranks[0]}\n')
            for k, v in self.private_ranks[1]:
                i += 1
                out.append(f'{i}. {k} - {v}\n')
        newline = '\n'
        return f'''

#### Rank since {self.period[0]} until {self.period[1]}
{''.join(out)}

### Moving Average
{self.moving_averageBranch.write()}

### Message distribution
People | Messages
--- | --- | ---
{f'{newline}'.join([f'{i[0]*100}% |{i[1]*100}%'
 for i in self.information_distribution])}

'''


class StartersRepliersIgnoredBranch:

    def __init__(self, people, calendar_arrays, tasks):
        self.starters: List[Tuple[str, int]] = {}
        self.repliers: List[Tuple[str, int]] = {}
        self.ignored: List[Tuple[str, int]] = {}
        # starters, repliers, ignored
        self.private_sris: List[Tuple[str, TriTuple]] = []
        self._get_conversation_starters(people,
                                        calendar_arrays,
                                        tasks['interval'])

    def _get_conversation_starters(
        self,
        message_dicts: List[Dict[str, Dict[int, List[Message]]]],
        calendar_arrays: List[Dict[str, np.array]],
        silent_time: int
    ) -> None:
        if len(calendar_arrays) == 1:
            # Group conversation
            self.starters, self.repliers, self.ignored = conversation_starters(
                message_dicts[0],
                calendar_arrays[0],
                silent_time=silent_time
            )
        else:
            # Private conversations
            for i, private_dict in enumerate(message_dicts):
                self.private_sris.append(
                    (get_different_key(
                        reader.my_name, private_dict.keys()
                    )[0],
                        conversation_starters(
                        private_dict,
                        calendar_arrays[i],
                        silent_time=silent_time
                    )
                    ))

    def write(self) -> str:
        section = '#### Starters, Repliers and Ignored\n'
        if self.private_sris:
            return f'{section}{self.write_private_sris()}'
        else:
            return f'{section}{self.write_group_sri()}'

    def write_private_sris(self):
        to_return: List[str] = []
        you_are_starter = []
        other_is_starter = []
        ratio_starter_you_per_other = []

        # Note tuple (name, (starter, replier, ignored))
        # starter, replier, ignored = List[Tulple[str, int]]
        for sri in self.private_sris:
            # starter
            if sri[0] == sri[1][0][0]:
                you_are_starter.append((sri[0], sri[1][0][0] / sri[1][1][0]))
                ratio_starter_you_per_other.append(
                    (sri[0], sri[1][0][1][1]
                     / (sri[1][0][1][1] + sri[1][0][0][1]))
                )
            else:
                other_is_starter.append((sri[0], sri[1][0][1]))
                ratio_starter_you_per_other.append(
                    (sri[0], sri[1][0][0][1]
                     / (sri[1][0][1][1] + sri[1][0][0][1]))
                )

        to_return.append("\nPeople with whom YOU start more conversations\n")
        for i, other, ntimes in enumerate(
            sorted(you_are_starter, key=lambda kv: kv[1])
        ):
            to_return.append(f'{i}. {other} {ntimes}\n')

        to_return.append("\nPeople who starts more conversations with you\n")
        for i, (other, ntimes) in enumerate(
            sorted(other_is_starter, key=lambda kv: kv[1])
        ):
            to_return.append(f'{i}. {other} {ntimes}\n')

        to_return.append("\nRatio who starts more you/other\n")
        for i, (other, times) in enumerate(
            sorted(ratio_starter_you_per_other, key=lambda kv: kv[1])
        ):
            to_return.append(f'{i}. {other} {times}\n')

        return ''.join(to_return)

    def write_group_sri(self):
        i = 1
        to_return: List[str] = []
        to_return.append("Conversation Starters (started conversations)\n")
        for k, v in self.starters:
            to_return.append(f'{i}. {k} {v}\n')
            i += 1

        to_return.append('\nTop Repliers (replied starters)\n')
        i = 1
        for k, v in self.repliers:
            to_return.append(f'{i}. {k} {v}\n')
            i += 1

        to_return.append('\nTop ignored (times ignored)\n')
        i = 1
        for k, v in self.ignored:
            to_return.append(f'{i}. {k} {v}\n')
            i += 1

        to_return.append('\nMost Notorious (% of time he/she was replied)\n')
        starters_dict = dict(self.starters)
        percentage_ignored = sorted(
            [(name, value / (value + starters_dict.get(name, 0)))
             for name, value in self.ignored],
            key=lambda kv: kv[1], reverse=False)

        i = 1
        for k, v in percentage_ignored:
            percentage = (1 - v) * 100
            to_return.append(f'{i} - {k} {percentage:,.1f}\n')
            i += 1

        return ''.join(to_return)


class HourlyFrequencyBranch:

    def __init__(self,
                 calendar_arrays: List[Dict[str, np.array]],
                 metadata: Dict[str, Any]):
        self.mean_by_hour: Dict[str, np.array]
        self.get_mean_by_hour(calendar_arrays, metadata)
        self.draw_hourly_mean_graph(metadata)

    def get_mean_by_hour(self,
                         calendar_array: List[Dict[str, np.array]],
                         metadata: Dict[str, Any]) -> None:
        self.mean_by_hour = get_mean_by_hour(join_calendars(
            calendar_array,
            metadata.get('sent_received_exchanged', 'exchanged'),
            reader.my_name))

    def draw_hourly_mean_graph(self, metadata: Dict[str, Any]):
        draw_hourly_mean(self.mean_by_hour, metadata)

    def write(self, criteria: str) -> str:
        to_return: List[str] = [
            f'#### Mean frequency of {criteria} per hour\n'
            f' Person | {":00 | ".join([str(t) for t in range(24)])}:00\n'
            f'--- {" | ---" * 24}\n'
        ]
        with open(
            os.path.join(
                reader.dirname, f'HourlyFrequency_{criteria}.csv'
            ),
            'w'
        ) as f:
            f.write(f'Time, {criteria} per hour;\n')
            for person, times in self.mean_by_hour.items():
                f.write(f'{person}, {", ".join([str(t) for t in times])};\n')
                to_return.append(
                    f' {person} | {"| ".join([f"{t:.3e}" for t in times])} \n'
                )
            to_return.append('\n')
        return ''.join(to_return)


class WeeklyFrequencyBranch:

    def __init__(self,
                 calendar_arrays: List[Dict[str, np.array]],
                 metadata: Dict[str, Any]):
        self.mean_by_week: Dict[str, np.array]
        self.get_mean_by_week(calendar_arrays)
        self.draw_weekly_mean_graph(metadata)

    def get_mean_by_week(self,
                         calendar_array: List[Dict[str, np.array]]) -> None:
        self.mean_by_week = get_mean_by_week(calendar_array[0])

    def draw_weekly_mean_graph(self, metadata: Dict[str, Any]):
        draw_weekly_mean(self.mean_by_week, metadata)

    def write(self, criteria: str):
        to_return: List[str] = [
            f'#### Mean frequency of {criteria} per week day\n'
            f'| Person | {":00 | ".join([str(t) for t in range(24)])}:00 |'
        ]
        with open(
            os.path.join(
                reader.dirname, f'WeeklyFrequency_{criteria}.csv'
            ),
            'w'
        ) as f:
            f.write(f'Time, {criteria} per week;\n')
            for person, days in self.mean_by_week.items():
                f.write(f'{person}, {", ".join([str(t) for t in days])};\n')
                to_return.append(
                    f'| {person} | {"| ".join([str(t) for t in days])} |'
                )
            to_return.append('\n')
        ''.join(to_return)


class ConversationAnalysisBranch:

    def __init__(self,
                 people: Dict[str, Dict[int, List[Message]]],
                 calendar_arrays: List[Dict[str, np.array]],
                 criteria: str,
                 tasks: Dict[str, Any]):
        self.criteria = criteria
        self.StartersRepliersIgnoredBranch: Optional[
            StartersRepliersIgnoredBranch] = None
        self.HourlyFrequencyBranch: Optional[HourlyFrequencyBranch] = None
        self.WeeklyFrequencyBranch: Optional[WeeklyFrequencyBranch] = None
        if v_tasks := tasks.get('starters_repliers_ignored'):
            self.get_starters_repliers_ignored(people,
                                               calendar_arrays,
                                               v_tasks)
        if v_tasks := tasks.get('hourly_frequency'):
            self.get_hourly_frequency(calendar_arrays, v_tasks)
        if v_tasks := tasks.get('weekly_frequency'):
            self.get_weekly_frequency(calendar_arrays, v_tasks)

    def get_starters_repliers_ignored(
        self,
        people: Dict[str, Dict[int, List[Message]]],
        calendar_arrays: List[Dict[str, np.array]],
        tasks: Dict[str, Any]
    ) -> None:
        self.StartersRepliersIgnoredBranch = StartersRepliersIgnoredBranch(
            people, calendar_arrays, tasks
        )

    def get_hourly_frequency(self, calendar_array, metadata):
        self.HourlyFrequencyBranch = HourlyFrequencyBranch(calendar_array,
                                                           metadata)

    def get_weekly_frequency(self, calendar_array, metadata):
        self.WeeklyFrequencyBranch = WeeklyFrequencyBranch(calendar_array,
                                                           metadata)

    def write(self):
        out = []
        if self.StartersRepliersIgnoredBranch:
            out.append(f'{self.StartersRepliersIgnoredBranch.write()}\n')
        if self.HourlyFrequencyBranch:
            out.append(f'{self.HourlyFrequencyBranch.write(self.criteria)}\n')
        if self.WeeklyFrequencyBranch:
            out.append(f'{self.WeeklyFrequencyBranch.write(self.criteria)}\n')

        return ''.join(out)


class messagesBranch:
    calendar_arrays: List[Dict[str, np.array]] = []
    rankBranch: Optional[rankBranch] = None
    conversationAnalysisBranch: Optional[ConversationAnalysisBranch] = None
    toFile: str

    def __init__(self,
                 messages_dicts: List[Dict[str, Dict[int, List[Message]]]],
                 tasks: Dict[str, Any]):
        self._get_calendar_arrays(messages_dicts)
        self.get_rankBranch(tasks)
        self.get_conversationAnalysisBranch(messages_dicts, tasks)

    @classmethod
    def _get_calendar_arrays(cls, messages_dicts) -> None:
        for messages_dict in messages_dicts:
            cls.calendar_arrays.append(
                info_per_hour_day(
                    messages_dict,
                    is_msg_criteria=True
                )
            )

    @classmethod
    def get_rankBranch(cls, tasks) -> None:
        if v_tasks := tasks.get('rank'):
            cls.rankBranch = rankBranch(cls.calendar_arrays,
                                        'messages',
                                        v_tasks)

    @classmethod
    def get_conversationAnalysisBranch(cls, messages_dicts, tasks) -> None:
        if v_tasks := tasks.get('conversation_analysis'):
            cls.conversationAnalysisBranch = ConversationAnalysisBranch(
                messages_dicts,
                cls.calendar_arrays,
                'messages',
                v_tasks
            )

    @classmethod
    async def write(cls):
        out: List[str] = []
        if cls.conversationAnalysisBranch:
            out.append(f'''
### Conversation Analysis
{cls.conversationAnalysisBranch.write()}
''')
        if cls.rankBranch:
            out.append(f'''
### Rank
{cls.rankBranch.write()}
''')

        cls.toFile = ''.join(out)
        print('\x1b[6;30;42mFinished write message branch\x1b[0m')


class wordsBranch:
    calendar_arrays: List[Dict[str, np.array]] = []
    conversationAnalysisBranch: Optional[ConversationAnalysisBranch] = None
    rankBranch: Optional[rankBranch] = None
    toFile: str

    def __init__(self, messages_dicts, tasks) -> None:
        self._get_calendar_arrays(messages_dicts)
        self.get_rankBranch(tasks)
        self.get_conversationAnalysisBranch(messages_dicts, tasks)

    @classmethod
    def _get_calendar_arrays(cls, messages_dicts) -> None:
        for messages_dict in messages_dicts:
            cls.calendar_arrays.append(
                info_per_hour_day(
                    messages_dict,
                    is_msg_criteria=False
                )
            )

    @classmethod
    def get_rankBranch(cls, tasks) -> None:
        if v_tasks := tasks.get('rank'):
            cls.rankBranch = rankBranch(cls.calendar_arrays,
                                        'words',
                                        v_tasks)

    @classmethod
    def get_conversationAnalysisBranch(cls, messages_dicts, tasks) -> None:
        if v_tasks := tasks.get('conversation_analysis'):
            cls.conversationAnalysisBranch = ConversationAnalysisBranch(
                messages_dicts,
                cls.calendar_arrays,
                'words',
                v_tasks
            )

    @classmethod
    async def write(cls):
        out: List[str] = []
        if cls.conversationAnalysisBranch:
            out.append(f'''
### Conversation Analysis
{cls.conversationAnalysisBranch.write()}
''')
        if cls.rankBranch:
            out.append(f'''
### Rank
{cls.rankBranch.write()}
''')

        cls.toFile = ''.join(out)
        print('\x1b[6;30;42mFinished write words branch\x1b[0m')


class reader:
    # TODO: use as cache
    messagesBranch: Optional[messagesBranch] = None
    wordsBranch: Optional[wordsBranch] = None
    messages_dicts: List[Dict[str, Dict[int, List[Message]]]] = []
    history_files: List[str] = []
    my_name: List[str] = []
    path_history_folder = ''
    dirname = ''

    def __init__(self, tasks: Dict[str, Any]):
        self._get_messages_dicts(tasks)
        asyncio.run(self.get_massage_and_word_statistics(tasks))

    @classmethod
    async def get_massage_and_word_statistics(cls, tasks):
        await asyncio.gather(
            cls.get_message_statistics(tasks),
            cls.get_word_statistics(tasks)
        )
        print('\x1b[6;30;42mFinished data processing.\x1b[0m'
              '\nWriting results...')

    @classmethod
    def _get_messages_dicts(
        cls,
        tasks: Dict[str, Any],
    ) -> None:
        cls.my_name = tasks['my_name']
        cls.path_history_folder = tasks['folder_containing_history']
        files = [file for file in os.listdir(cls.path_history_folder)
                 if file[-4:] == '.txt' and file not in cls.history_files]
        if files:
            cls.history_files = files + cls.history_files
        else:
            return

        for file in cls.history_files:
            try:
                with open(
                    f'{cls.path_history_folder}/{file}', 'r',
                ) as history_file:
                    cls.messages_dicts.append(
                        leitor(history_file, tasks['merge_similar_names'])
                    )
            except UnicodeDecodeError:
                log2console('\x1b[0;30;43mWARNING: Failed decoding with utf-8,'
                            'trying ISO-8859-1...\x1b[0m')
                with open(
                    f'{cls.path_history_folder}/{file}',
                    'r',
                    encoding='ISO-8859-1'
                ) as history_file:
                    cls.messages_dicts.append(
                        leitor(history_file, tasks['merge_similar_names'])
                    )
        return

    @classmethod
    async def get_message_statistics(cls, tasks: Dict[str, Any]) -> None:
        if v_messages := tasks.get('messages'):
            cls.messagesBranch = messagesBranch(cls.messages_dicts,
                                                v_messages)

    @classmethod
    async def get_word_statistics(cls, tasks: Dict[str, Any]) -> None:
        if v_words := tasks.get('words'):
            cls.wordsBranch = wordsBranch(cls.messages_dicts, v_words)

    @classmethod
    def write_results(cls, dirname) -> None:
        cls.dirname = dirname
        asyncio.run(cls._write_messages_and_words_statistics())
        with open(os.path.join(dirname, 'Results.md'), 'w') as file:
            file.write(f'''
# Whatsapp Statistics Results

Results for {cls.path_history_folder}

## Messages analysis

''')
            file.write(messagesBranch.toFile)
            file.write('\n## Words analysis\n')
            file.write(wordsBranch.toFile)
            messagesBranch.toFile = ''
            wordsBranch.toFile = ''
        show()

    @classmethod
    async def _write_messages_and_words_statistics(cls):
        await asyncio.gather(messagesBranch.write(),
                             wordsBranch.write())
