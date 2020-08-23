
from datetime import date, datetime, timedelta
import time


def concatenate_h(fname1, fname2,ling):

    # ling = int(input('In which language was the smatphone? Enter 1 for PT or EN, enter 2 for DE, enter 3 for FR.\n'))
    aux1 = 0
    if ling == 3:
        aux1 = 1

    f1 = open(fname1,'r')
    f2 = open(fname1,'r')

    # Discover the first file
    ini_dates = []
    for line in f1:
        line2 = line.replace("\u200e","")
        palavras = line2.split()
        #verifica se é mensagem
        if len(palavras) > 4 and palavras[3][0:1] != '\u200e':
            # verifica se há data
            if palavras[0][0:2].isdigit() and palavras[1][0:2].isdigit() and palavras[2+aux1] == '-':
                # obtém a data da primeria mensagem
                if ling == 2:
                    data0 = date(int(palavras[0][6:8]) + 2000, int(palavras[0][3:5]), int(palavras[0][0:2]))
                elif ling == 1:
                    data0 = date(int(palavras[0][6:10]), int(palavras[0][3:5]), int(palavras[0][0:2]))
                ini_dates.append(data0)
                break

    for line in f2:
        line2 = line.replace("\u200e","")
        palavras = line2.split()
        #verifica se é mensagem
        if len(palavras) > 4 and palavras[3][0:1] != '\u200e':
            # verifica se há data
            if palavras[0][0:2].isdigit() and palavras[1][0:2].isdigit() and palavras[2+aux1] == '-':
                # obtém a data da primeria mensagem
                if ling == 2:
                    data0 = date(int(palavras[0][6:8]) + 2000, int(palavras[0][3:5]), int(palavras[0][0:2]))
                elif ling == 1:
                    data0 = date(int(palavras[0][6:10]), int(palavras[0][3:5]), int(palavras[0][0:2]))
                ini_dates.append(data0)
                break

    fout = open("hist_merged.txt",'w')
    if ini_dates[0] < ini_dates[1]:
        for line in f1:
            line2 = line.replace("\u200e","")
            palavras = line2.split()
            #verifica se é mensagem
            if len(palavras) > 4 and palavras[3][0:1] != '\u200e':
                # verifica se há data
                if palavras[0][0:2].isdigit() and palavras[1][0:2].isdigit() and palavras[2+aux1] == '-':
                    # obtém a data da primeria mensagem
                    if ling == 2:
                        data0 = date(int(palavras[0][6:8]) + 2000, int(palavras[0][3:5]), int(palavras[0][0:2]))
                    elif ling == 1:
                        data0 = date(int(palavras[0][6:10]), int(palavras[0][3:5]), int(palavras[0][0:2]))
                    if data0 >= ini_dates[1]: 
                        break
            fout.write(line2)
        for line in f2:
            line2 = line.replace("\u200e","")
            fout.write(line2)
    else:
        for line in f2:
            line2 = line.replace("\u200e","")
            palavras = line2.split()
            #verifica se é mensagem
            if len(palavras) > 4 and palavras[3][0:1] != '\u200e':
                # verifica se há data
                if palavras[0][0:2].isdigit() and palavras[1][0:2].isdigit() and palavras[2+aux1] == '-':
                    # obtém a data da primeria mensagem
                    if ling == 2:
                        data0 = date(int(palavras[0][6:8]) + 2000, int(palavras[0][3:5]), int(palavras[0][0:2]))
                    elif ling == 1:
                        data0 = date(int(palavras[0][6:10]), int(palavras[0][3:5]), int(palavras[0][0:2]))
                    if data0 >= ini_dates[1]: 
                        break
            fout.write(line2)
        for line in f1:
            line2 = line.replace("\u200e","")
            fout.write(line2)
    f1.close()
    f2.close()
    fout.close()
    print("Saved hist_merged.txt\n")

print("This program concatenates two files of history of the same conversation.\n")
print("It is useful when you want to merge a recent history with an older one.\n")

file1 = input("Enter the first file\n")
file2 = input("Enter a second file\n")
ling = int(input('In which language was the smatphone? Enter 1 for PT or EN, enter 2 for DE, enter 3 for FR.\n'))
concatenate_h(file1,file1,ling)