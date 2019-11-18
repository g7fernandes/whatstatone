import numpy as np 
import matplotlib.pyplot as plt 
import matplotlib.dates as mdates
from datetime import date, datetime, timedelta
import time

def nome(p):
    i = 3
    nome = ""
    aux = True
   
    while p[i][-1] != ":":
        nome = nome + p[i] + " "
        i += 1
        if (len(p)) >= i:
            break
    
    if p[i][-1] == ":":
        aux = False

    nome = nome + p[i]
    nome = nome.replace(":","")
    if aux or len(nome) > 50:
        nome = " "
    return nome

dia = 3600*12

fname = input("Enter the name or the path to the file of the exported conversation:\n")

ling = int(input('In which language was the smatphone? Enter 1 for PT or EN, enter 2 for DE, enter 3 for FR.\n'))
aux1 = 0
if ling == 3:
    aux1 = 1

pessoa = []
nmsg1 = [] #numero de mensagens da pessoa 1
nmsg2 = [] #numero de mensagens da pessoa 2

print("The name of the people in the chat must have less than 50 characters, if not, will not work properly.\n")

lista_dias = []

d = 0
with open(fname) as f:
    for line in f:
        palavras = line.split()
        #verifica se é mensagem
        if len(palavras) > 4 and palavras[3][0:1] != '\u200e':
            # verifica se há data
            if palavras[0][0:2].isdigit() and palavras[1][0:2].isdigit() and palavras[2+aux1] == '-':
                # identifica as pessoas
                if len(pessoa) < 2:
                    name = nome(palavras)
                    if name != " ":
                        if len(pessoa) == 0:
                            pessoa.append(name)
                        elif pessoa[0] != name:
                            pessoa.append(name)
                # obtém a data da primeria mensagem
                if ling == 2:
                    if len(nmsg1) == 0 and len(nmsg2) == 0:
                        data0 = date(int(palavras[0][6:8]) + 2000, int(palavras[0][3:5]), int(palavras[0][0:2]))
                        data_ant = data0
                        nmsg1.append(0)
                        nmsg2.append(0)
                    else:
                        data = date(int(palavras[0][6:8]) + 2000, int(palavras[0][3:5]), int(palavras[0][0:2]))
                        tl = data - data_ant 
                        # verifica se passaram dias entre as mensagens
                        if tl.total_seconds()/86400 >= 1:
                            for i in range(int(tl.total_seconds()/86400)):
                                nmsg1.append(0)
                                nmsg2.append(0)
                                d += 1
                                lista_dias.append(data_ant + timedelta(days=i))
                        data_ant = data
                elif ling == 1:
                    if len(nmsg1) == 0 and len(nmsg2) == 0:
                        data0 = date(int(palavras[0][6:10]), int(palavras[0][3:5]), int(palavras[0][0:2]))
                        data_ant = data0
                        nmsg1.append(0)
                        nmsg2.append(0)
                    else:
                        data = date(int(palavras[0][6:10]), int(palavras[0][3:5]), int(palavras[0][0:2]))
                        tl = data - data_ant 
                        # verifica se passaram dias entre as mensagens
                        if tl.total_seconds()/86400 >= 1:
                            for i in range(int(tl.total_seconds()/86400)):
                                nmsg1.append(0)
                                nmsg2.append(0)
                                d += 1
                                lista_dias.append(data_ant + timedelta(days=i))
                        data_ant = data


                # Adiciona mensagem a posição d referente ao dia após data0
                if (len(pessoa) > 0):
                    name = nome(palavras)
                    if name == pessoa[0]:
                        nmsg1[d] += 1
                    elif name == pessoa[1]:
                        nmsg2[d] += 1
    lista_dias.append(data)

nmsg1 = np.array(nmsg1)
nmsg2 = np.array(nmsg2)
p1 = []
p2 = []

ans = input("Make graph [y/n]? ")
while ans == "y" or ans == "Y":
    ans = input("A graph of messages per day will be build.\nEnter a interval to average [1]: ")
    if ans == " ":
        ans = 1
        p1 = nmsg1
        p2 = nmsg2
    else:
        ans = int(ans)
        for i in range(len(nmsg1)):
            if i < len(nmsg1) - ans:
                p1.append(np.sum(nmsg1[i:i+ans]))
                p2.append(np.sum(nmsg2[i:i+ans]))
            else:
                p1.append(np.sum(nmsg1[i:i+ans]))
                p2.append(np.sum(nmsg2[i-ans:i]))
        p1 = np.array(p1)/ans
        p2 = np.array(p2)/ans

#%% PLOT #

    days = mdates.DayLocator()
    # years = mdates.YearLocator(interval=30)   # every year
    months = mdates.MonthLocator()  # every month


    dates = mdates.num2date(mdates.drange(data0, data + timedelta(days=1), timedelta(days=1)))

    plt.figure(1)
    plt.gca().plot(dates,p1,label=pessoa[0])
    plt.gca().plot(dates,p2,label=pessoa[1])
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
    plt.gca().xaxis.set_minor_locator(days)
    # plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_locator(months)
    plt.gca().set_title("Messages per day average each {} days".format(ans))
    plt.legend()
    plt.gcf().autofmt_xdate()

    plt.figure(2)
    plt.gca().plot(dates,p1+p2)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
    plt.gca().xaxis.set_minor_locator(days)
    # plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_locator(months)
    plt.gca().set_title("Messages per day average each {} days".format(ans))
    plt.gcf().autofmt_xdate()

    plt.show()

    ans = input("Make another graph [y/n]? ")


ans = input("Export csv with data? [y/n]")

if ans == "y" or ans == "Y":
    with open(fname[0:len(fname)-4]+"_result.csv", "w") as f:
        f.write("{}, {}, date\n".format(pessoa[0], pessoa[1]))
        for i in range(len(nmsg1)):
            f.write("{}, {}, {}\n".format(nmsg1[i],nmsg2[i],lista_dias[i]))

print("Saved file {}\n".format(fname[0:len(fname)-4]+"_result.csv"))