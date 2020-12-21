import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import matplotlib
import numpy as np
from reader import Message, fit_dates_to_history_time_length
from datetime import datetime, timedelta
from typing import (List, Dict, Any, Tuple, Union,
                    ItemsView, Iterable, Optional)
from utils import get_dates
from itertools import cycle
import progressbar
import pandas as pd
import bar_chart_race as bcr
import os


colors = ["#adb0ff", "#ffb3ff", "#90d595", "#e48381",
          "#aafbff", "#f7bb5f", "#eafb50", "#d0ff8a"]

DataCollection = Union[ItemsView[str, float], List[Tuple[str, float]]]


def filter_data_to_plot(
    data: Union[Iterable, DataCollection],
    keys2plot: List['str'],
    max_number: Optional[int] = None
) -> List[Tuple[str, np.ndarray]]:
    filtered_data: List[Tuple[str, np.ndarray]] = []

    enqueue: List[Tuple[str, np.ndarray]] = []
    if max_number is None:
        max_number = len(keys2plot)
    for k, v in data:
        enqueue.append((k, v))
        if k in keys2plot:
            if max_number:
                max_number -= 1
            filtered_data.append((k, v))
    for k, v in enqueue:
        if abs(max_number) > 0:
            if max_number:
                filtered_data.append((k, v))
                max_number -= 1
    return filtered_data


def draw_hourly_mean(
    data_dict: Dict[str, np.ndarray],
    metadata: Dict[str, Any]
):
    fig, ax = plt.subplots(figsize=(15, 8), constrained_layout=True)

    filtered: List[Tuple] = []
    if curves_to_plot := metadata.get('plot_keys'):
        filtered = [(k, v) for k, v in data_dict.items()
                    if k in curves_to_plot]

    if metadata.get('plot_total') or len(filtered) == 0:
        filtered.append(('Total', data_dict['TOTAL']))

    hours = ['3:00', '4:00', '5:00', '6:00', '7:00', '8:00',
             '9:00', '10:00', '11:00', '12:00', '13:00', '14:00',
             '15:00', '16:00', '17:00', '18:00', '19:00', '20:00',
             '21:00', '22:00', '23:00', '00:00', '1:00', '2:00']

    ax.set_title(metadata['title'])
    for k, v in filtered:
        ax.plot(hours, np.concatenate((v[3:24], v[:3])), label=k)
    ax.legend()
    ax.grid(True)


def draw_weekly_mean(
    data_dict: Dict[str, np.ndarray],
    metadata: Dict[str, Any]
):
    fig, ax = plt.subplots(figsize=(15, 8), constrained_layout=True)

    curves_to_plot = metadata.get('plot_keys')
    if not isinstance(curves_to_plot, List):
        raise SystemExit('Names to plot must be list of string')

    if metadata.get('plot_total') or not curves_to_plot:
        curves_to_plot.append('TOTAL')

    filtered: List[Tuple[str, np.ndarray]] = filter_data_to_plot(
        data_dict.items(),
        curves_to_plot
    )

    days = ['.Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun', 'Mon.']

    ax.set_title(metadata['title'])
    for k, v in filtered:
        ax.plot(days, np.concatenate((v[6:7], v, v[0:1])), label=k)
    ax.legend()
    ax.grid(True)
    plt.show()


def get_anex_data(
    data_dict: Union[List[Tuple[str, np.ndarray]], Dict[str, np.ndarray]]
) -> Optional[Tuple[datetime, datetime]]:
    if isinstance(data_dict, dict):
        for i, (k, v) in enumerate(data_dict.items()):
            if k == 'init_and_final_times':
                init_date = v[0]
                final_date = v[1]
                data_dict.pop(k)
                return (init_date, final_date)
    elif isinstance(data_dict, list):
        for i, (k, v) in enumerate(data_dict):
            if k == 'init_and_final_times':
                init_date = v[0]
                final_date = v[1]
                data_dict.pop(i)
                return (init_date, final_date)
    return None


def draw_line_chart(
    data_dict: Union[List[Tuple[str, np.ndarray]], Dict[str, np.ndarray]],
    init_date: datetime,
    final_date: datetime,
    metadata: Dict[str, Any],
    fig=None,
    ax=None
) -> None:

    anex_data = get_anex_data(data_dict)
    if anex_data:
        (init_date, final_date) = anex_data

    (start, final) = fit_dates_to_history_time_length(init_date, final_date)

    plt.clf()
    if not fig or not ax:
        fig, ax = plt.subplots(figsize=(15, 8))
    ax.clear()

    locator = mdates.AutoDateLocator(minticks=3, maxticks=10)
    formater = mdates.ConciseDateFormatter(locator)
    dates = get_dates(init_date, final_date)

    max_names_per_graph = metadata.get('max_names_per_graph', 0)

    curves_to_plot = metadata.get('plot_keys', [''])
    if not isinstance(curves_to_plot, list):
        raise SystemExit('The names to plot should be list of strings')
    if isinstance(data_dict, dict):
        data_dict = [(k, v) for k, v in data_dict.items()]

    filtered_data_dicts: List[Tuple[str, np.ndarray]]

    if metadata.get('plot_total'):
        curves_to_plot.append('TOTAL')

    filtered_data_dicts = filter_data_to_plot(
        sorted(data_dict,
               key=lambda kv: np.sum(kv[1]),
               reverse=True
               )[:max_names_per_graph],
        curves_to_plot,
        max_names_per_graph
    )

    if metadata.get('plot_total'):
        ax2 = ax.twinx()
        ax2.clear()
        ax2.set_ylabel('Total')

    delay = len(dates[:final]) - len(filtered_data_dicts[0][1][start:final])  # type: ignore # noqa
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formater)
    for name, info in filtered_data_dicts:
        if name == 'TOTAL':
            ax2.xaxis.set_major_locator(locator)
            ax2.xaxis.set_major_formatter(formater)
            ax2.plot(dates[delay:final],
                     info[start:final],
                     label=name,
                     color='k',
                     linewidth=1)
            continue
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formater)
        ax.plot(dates[delay:final], info[start:final], label=name)
    ax.set_title(metadata['title'])
    ax.grid(True)
    fig.legend()


def draw_barchart(
    data_dict: Union[ItemsView[str, float], List[Tuple[str, float]]],
    metadata: Dict[str, Any],
    fig=None,
    ax=None
) -> None:
    max_names = 257
    if not fig or not ax:
        fig, ax = plt.subplots(figsize=(15, 8))
        max_names = metadata.get('max_names_per_graph', 10)
    ax.clear()

    if metadata.get('association_name_color') is None:
        color_iter = cycle(colors)
        metadata['association_name_color'] = {
            name: next(color_iter) for name, _ in data_dict
        }

    if max_names > len(data_dict):
        max_names = len(data_dict)

    ax.barh(
        [item[0] for item in data_dict][:max_names],
        [item[1] for item in data_dict][:max_names],
        color=[metadata.get('association_name_color')[item[0]]  # type: ignore
               for item in data_dict][:max_names]
    )

    dx = max([item[1] for item in data_dict][:max_names]) / 200

    for i, (name, value) in enumerate(data_dict):
        if i >= max_names:
            break
        ax.text(value - dx, i, name, size=14,
                weight=600, ha='right', va='bottom')
        ax.text(value + dx, i, f'{value:,.0f}',
                size=14, ha='left', va='center')
    ax.text(1, 0.4, metadata['background_text'], transform=ax.transAxes,
            color='#777777', size=34, va='bottom', ha='right', weight=800)
    ax.text(0, 1.06, metadata['subtitle'],
            transform=ax.transAxes, size=12, color='#777777')
    ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
    ax.xaxis.set_ticks_position('top')
    ax.tick_params(axis='x', colors='#777777', labelsize=12)
    ax.set_yticks([])
    ax.margins(0, 0.01)
    ax.grid(which='major', axis='x', linestyle='-')
    ax.set_axisbelow(True)
    ax.text(0, 1.15, metadata['title'],
            transform=ax.transAxes, size=24, weight=600, ha='left', va='top')
    # 'by @g7fernandes; credit @jburnmurdoch'
    ax.text(1, 0, metadata['footer'],
            transform=ax.transAxes, color='#777777', ha='right',
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='white'))
    plt.box(False)


def animate(draw_fun,
            data_dict: Dict[str, np.ndarray],
            metadata,
            savedir: str,
            plot_type: str = 'bar',
            fargs: Optional[Tuple] = None):

    fig, ax = plt.subplots(figsize=metadata['figsize'])  # (15, 8)
    ax.clear()

    color_iter = cycle(colors)
    metadata['association_name_color'] = {
        name: next(color_iter) for name in data_dict.keys()
    }

    ndays = len(next(iter(data_dict.values())))

    step = metadata['animation']['step']
    data_at_time = []
    day = 0
    for day in range(0, ndays, step):
        if plot_type == 'line':
            data_at_time.append([
                (k, v[0:day + 1])
                for k, v in data_dict.items()
            ])
            data_at_time[-1].append(
                ('init_and_final_times',
                 [fargs[0], fargs[0] + timedelta(day + 1)])  # type: ignore
            )
        else:
            data_at_time.append([(k, v[day]) for k, v in data_dict.items()])
        metadata['background_text'] = (Message.initial_date
                                       + timedelta(days=day))

    if plot_type == 'bar':
        data_at_time = [
            sorted(
                data,
                key=lambda kv:kv[1], reverse=True
            )[:metadata['max_names_per_graph']] for data in data_at_time
        ]

    pbar = progressbar.ProgressBar(max_value=len(data_at_time))
    count = [0]

    def add_progression_bar(*args):
        pbar.update(count[0])
        count[0] += 1
        metadata['background_text'] = Message.initial_date + \
            timedelta(days=step * count[0])
        draw_fun(*args, metadata=metadata, fig=fig, ax=ax)

    animator = matplotlib.animation.FuncAnimation(  # type: ignore
        fig,
        add_progression_bar,
        frames=data_at_time,
        interval=int(1000 / metadata['animation']['fps']),
        fargs=fargs
    )

    print("Saving... (may take a while)\n")
    animator.save(
        os.path.join(savedir, f'{metadata["title"]}.mp4'),
        writer="ffmpeg"
    )


def animate_better_barchart(data_dict: Dict[str, np.ndarray],
                            metadata: Dict[str, Any],
                            savedir: str):
    dates = get_dates(Message.initial_date, Message.final_date)
    df = pd.DataFrame.from_dict(data_dict)
    df.index = dates
    bcr.bar_chart_race(
        df,
        n_bars=metadata['max_names_per_graph'],
        steps_per_period=metadata['animation']['fps'],
        title=metadata['title'],
        filename=os.path.join(savedir, f'{metadata["title"]}.mp4'),
        period_length=metadata['animation']['bcr_period']
    )


def plot_zipf(data: np.ndarray, criteria: str):
    fig, ax = plt.subplots(constrained_layout=True)
    ax.plot(data[:, 0] * 100, data[:, 1] * 100)
    ax.set_xlabel('% of people')
    ax.set_ylabel(f'% of {criteria}')
    ax.set(title=f'Distribution of {criteria} among people')
    ax.grid(True)
