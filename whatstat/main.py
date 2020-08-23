#!/usr/bin/env python3
import os
from history_reader import (leitor_msg, leitor_words,
                            leitor_msg_group, leitor_words_group)
import pandas as pd
import shutil
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.animation as animation


try:
    import progressbar
    pbar = True
except ModuleNotFoundError:
    print('Warning: progressbar not available. Try one:')
    print('conda install -c conda-forge progressbar2')
    print('conda install -c conda-forge/label/gcc7 progressbar2')
    print("or search for the pip package")
    pbar = False

a = '2'
if os.path.exists('concat.csv'):
    print("The file with quantity of messages or words concat.csv exists.\n")
    while a != "1" and a != "0":
        a = input(
            "Do you wish to use this file [0] or read again the backup files [1]?"
            "\nEnter 1 or 0: ")
else:
    a = '1'


arc_tipo = " exchanged "
tipo = "c"
if a == '1':
    print("In order to save the animation, you must have ffmpeg installed! \n"
          "Export .txt conversation backup files from whatsapp, nname them\n"
          "with the name of the person with of each backup and put in a\n"
          "folder named 'msg'.\n"
          "If you want to want to rank the messages of group conversation,\n"
          "save the backup file at the same directory of main.py\n")

    # Language of the smatphone. Important to read date and time correctly.

    language = input(
        'In which language was the smatphone? '
        'Enter 1 for PT or EN, enter 2 for DE, enter 3 for FR.\n')
    language = int(language)
    aux1 = 0
    if language == 3:
        aux1 = 1

    print("The name of the people in the chat must have less than "
          "50 characters, if not, will not work properly.\n")

    criterio = "messages"
    aux2 = input(
        "Use number of messages [1] or number of words [2] in the graph?\n"
        "Enter 1 or 2: ")
    if aux2 == "2":
        criterio = "words"

    aux2 = input(
        "Read a group conversation [1] "
        "or invididual priviate conversations?[2]"
        "\nEnter 1 or 2: ")
    if aux2 == "2":
        # Find the directory where the files are
        people = os.listdir('msg')

        # process files
        if os.path.exists('results'):
            shutil.rmtree('results')
        os.mkdir('results')  # create results folder

        aux = True
        for person in people:
            if criterio == "messages":
                last_date = leitor_msg('msg/' + person, person, language)
            else:
                last_date = leitor_words('msg/' + person, person, language)
            if aux:
                last_datemax = last_date
                aux = False
            if last_datemax < last_date:
                last_datemax = last_date

        print("All messages computed!"
              "\nBuilding Data Frame of cumulative messages...")
    elif aux2 == "1":
        arc_tipo = " sent "
        tipo = input(
            "What kind of plot do you want? Enter\n"
            "c   for cumulative\n
            "w   for weekly frequency\n
            "q   for biweekly frequency\nm   for monthly\n")
        # process files
        if os.path.exists('results'):
            shutil.rmtree('results')
        os.mkdir('results')  # create results folder

        fname = input("Enter the name of the backup file:\n")
        if not os.path.exists(fname):
            print("=== File does not exist! ===")
        if criterio == "messages":
            last_date = leitor_msg_group(fname, language, tipo)
        else:
            print("Critério Words group")
            last_date = leitor_words_group(fname, language, tipo)
        with open('membros_list.txt', 'r') as f:
            people = []
            for line in f:
                people.append(line)
            for i in range(len(people)):
                people[i] = people[i].replace("\n", "") + ".txt"
    # %%
    # read cumulative number of messages file to one file
    print("Fillanguage lacking dates (may take a while)...\n")
    aux = True
    for person in people:
        if aux:
            cum_tot = pd.read_csv(
                'results/' + person[0:len(person)-4] + "_result.csv")
            aux = False
        else:
            cum_par = pd.read_csv(
                'results/' + person[0:len(person)-4] + "_result.csv")
            cum_tot = pd.concat([cum_tot, cum_par])

    del cum_par

    cum_tot = cum_tot.reset_index(drop=True)

    dates = cum_tot['date'].values.tolist()
    dates = list(dict.fromkeys(dates))
    dates.sort()

    i = 1
    if pbar:
        bar = progressbar.ProgressBar(max_value=len(cum_tot))
    while i < len(cum_tot):
        if pbar:
            bar.update(i)
        # enche as datas até o final
        if cum_tot['name'][i] != cum_tot['name'][i-1]:  # mudou de nome
            if cum_tot['date'][i-1] != last_date:
                ld_current = dates.index(cum_tot['date'][i-1])
                line = cum_tot.iloc[[i-1]].copy()
                for j in range(ld_current+1, len(dates)):
                    line['date'] = dates[j]
                    cum_tot = pd.concat(
                        [cum_tot.iloc[:i-1], line, cum_tot.iloc[i:]]).reset_index(drop=True)
                    i += 1
        # adiciona datas faltantes
        else:
            ld_current = dates.index(cum_tot['date'][i-1])
            while dates[ld_current+1] < cum_tot['date'][i]:
                line = cum_tot.iloc[[i-1]].copy()
                line['date'] = dates[ld_current + 1]
                ld_current += 1
                cum_tot = pd.concat(
                    [cum_tot.iloc[:i-1], line, cum_tot.iloc[i:]]).reset_index(drop=True)
                i += 1
        i += 1

    # cum_tot.to_csv("concat.csv")
    cum_tot.to_csv("concat.csv", index=False)

else:
    criterio = "messages"
    aux2 = input(
        "Use number of messages [1] or number of words [2] in the graph?\nEnter 1 or 2: ")
    if aux2 == "2":
        criterio = "words"
    cum_tot = pd.read_csv("concat.csv")
    dates = cum_tot['date'].values.tolist()
    dates = list(dict.fromkeys(dates))
    if os.path.exists('membros_list.txt'):
        with open('membros_list.txt', 'r') as f:
            people = []
            for line in f:
                people.append(line)
            for i in range(len(people)):
                people[i] = people[i].replace("\n", "") + ".txt"
    dates.sort()

#%% PLOT #
# BAR CHART ADAPTAR

# Cores
colors = dict(zip(
    ["1", "2", "3", "4", "5", "6", "7"],
    ["#adb0ff", "#ffb3ff", "#90d595", "#e48381", "#aafbff", "#f7bb5f", "#eafb50"]
))

group = []
j = 1
for i in range(len(cum_tot)):
    nm = cum_tot['name'][i]
    if i == 0:
        group.append(str(j))
        nm0 = nm
    else:
        if nm == nm0:
            group.append(str(j))
        else:
            j += 1
            if j > 7:
                j = 1
            group.append(str(j))
            nm0 = nm


group = pd.DataFrame(data=group, columns=["group"])
cum_tot = pd.concat([cum_tot, group], axis=1)


for i in range(len(cum_tot)):
    cum_tot.at[i, "name"] = cum_tot["name"].iloc[i].replace("_", " ")
    cum_tot.at[i, "date"] = cum_tot["date"].iloc[i].replace(
        "00", "20")  # case whastapp exported date in the format yy-mm-dd
for i in range(len(dates)):
    # case whastapp exported date in the format yy-mm-dd
    dates[i] = dates[i].replace("00", "20")

group_lk = cum_tot.set_index('name')['group'].to_dict()


# cria plot
fig, ax = plt.subplots(figsize=(15, 8))
# função
if tipo == "w":
    criterio = criterio + " per week"
elif tipo == "m":
    criterio = criterio + " per month"
elif tipo == "q":
    criterio = criterio + " per 15 days"


def draw_barchart(current_date, criterio):
    dff = cum_tot[cum_tot['date'].eq(current_date)].sort_values(
        by='value', ascending=True).tail(10)
    ax.clear()
    ax.barh(dff['name'], dff['value'], color=[colors[group_lk[x]]
                                              for x in dff['name']])
    dx = dff['value'].max() / 200
    for i, (value, name) in enumerate(zip(dff['value'], dff['name'])):
        ax.text(value-dx, i,     name,           size=14,
                weight=600, ha='right', va='bottom')
        ax.text(value+dx, i,     f'{value:,.0f}',
                size=14, ha='left',  va='center')
    ax.text(1, 0.4, current_date, transform=ax.transAxes,
            color='#777777', size=34, va='bottom', ha='right', weight=800)
    ax.text(0, 1.06, criterio, transform=ax.transAxes, size=12, color='#777777')
    ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
    ax.xaxis.set_ticks_position('top')
    ax.tick_params(axis='x', colors='#777777', labelsize=12)
    ax.set_yticks([])
    ax.margins(0, 0.01)
    ax.grid(which='major', axis='x', linestyle='-')
    ax.set_axisbelow(True)
    ax.text(0, 1.15, 'People that' + arc_tipo + 'more ' + criterio,
            transform=ax.transAxes, size=24, weight=600, ha='left', va='top')
    ax.text(1, 0, 'by @g7fernandes; credit @jburnmurdoch', transform=ax.transAxes, color='#777777', ha='right',
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='white'))
    plt.box(False)


print("Creating animation\n")
fig, ax = plt.subplots(figsize=(15, 8))
print("There are {} days of history.\n".format(len(dates)))
jump = int(
    input("Plot in intervals of how many days? [enter integer larger or equal 1]\n"))
if jump > 1:
    dates2 = dates
    dates = []
    i = 0
    for dia in dates2:
        if i == 0 or dia == dates2[-1]:
            dates.append(dia)
        elif i == jump:
            i == 0
        else:
            i += 1

aux = input("make video using matplotlib? [y/n] ")
if aux == "y":
    fps = int(input("Enter a number of frames per second: "))
    animator = animation.FuncAnimation(
        fig, draw_barchart, frames=dates, fargs=(criterio,), interval=int(1000/fps))
    print("Saving... (may take a while)\n")
    animator.save(criterio + "_animated_chart.mp4", writer="ffmpeg")
    print("Saved animated_chart.mp4\n")
# HTML(animator.to_jshtml()) or use animator.to_html5_video() or animator.save()

aux = input("Export database for R [y/n]? ")
N = [x for x in range(1, len(people)+1)]
if not aux == "n":
    cont = 0
    if pbar:
        bar = progressbar.ProgressBar(max_value=len(dates))
    for current_date in dates:
        if pbar:
            bar.update(i)
        if cont == 0:
            df2R = cum_tot[cum_tot['date'].eq(current_date)].sort_values(
                by='value', ascending=True)  # .tail(10)
            df2R.insert(0, "rank", N, True)
        else:
            df2R_aux = cum_tot[cum_tot['date'].eq(current_date)].sort_values(
                by='value', ascending=True)  # .tail(10)
            df2R_aux.insert(0, "rank", N, True)
            df2R = pd.concat([df2R, df2R_aux])
        cont += 1

    df2R.to_csv("database4R.csv", index=False)

if tipo == "c":
    aux = "y"
while not aux == 'n':
    if tipo == "c":
        print("Let's build a rank! First message: {} Last message: {}\n".format(
            dates[0], dates[-1]))
        ini_date = input("Enter initial date (format yyyy-mm-dd)\n")
        final_date = input("Enter final date (format yyyy-mm-dd)\n")
        df2R = cum_tot[cum_tot["date"].eq(ini_date)].sort_values(
            by='name', ascending=True)
        df2R = df2R.reset_index(drop=True)
        df2R_aux = cum_tot[cum_tot["date"].eq(final_date)].sort_values(
            by='name', ascending=True)
        df2R_aux = df2R_aux.reset_index(drop=True)
        df2R["value"] = df2R_aux["value"] - df2R["value"]
        df2R = df2R.sort_values(by='value', ascending=False)
        df2R = df2R.reset_index(drop=True)
        df2R.to_csv("rank"+arc_tipo+criterio+".csv",
                    columns=["name", "value", "date"])
        print("*Rank | Name | nmsg*")
        for line in range(len(df2R)):
            print("{:3d} {} - {}".format(line+1,
                                         df2R["name"].iloc[line], df2R["value"].iloc[line]))
        aux = input("Do rank with other dates? [y/n]")

if os.path.exists('results'):
    shutil.rmtree('results')
