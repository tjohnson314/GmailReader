
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime

def queryWithKeyword(c, substr):
    print("Querying: " + substr)
    times = []
    for row in c.execute('SELECT * FROM texts WHERE data LIKE ?', (substr,)):
        times.append(int(row[0]))

    return times


def testDayOfWeek(c):
    week = [0]*7
    for row in c.execute('SELECT * FROM texts'):
        day = int(row[0])/(3600*24)
        week[day%7] += 1

    plt.bar(range(len(week)), week)
    plt.show()


def toDays(times):
    start = datetime(2015, 7, 3)
    startTimestamp = (start - datetime(1970, 1, 1)).total_seconds()
    end = datetime.now()
    endTimestamp = (end - datetime(1970, 1, 1)).total_seconds()
    totalDays = int(endTimestamp - startTimestamp)/(3600*24) + 1
    days = [0]*totalDays

    for t in times:
        day = int(t - startTimestamp)/(3600*24)
        #print(day)
        days[day] += 1

    return days


def makePlot(lst, searchString):
    plt.bar(range(len(lst)), lst)
    plt.xlabel("Days since July 3rd, 2015")
    plt.ylabel("Texts containing \"" + searchString + "\"")
    plt.show()


def search(c, searchString):
    times = queryWithKeyword(c, '%' + searchString + '%')
    days = toDays(times)
    makePlot(days, searchString)

def main():
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    #search(c, 'I love you')
    testDayOfWeek(c)
    conn.close()

if __name__ == '__main__':
    main()