import csv
import matplotlib.pyplot as plt
import datetime

input_file = open(r'F:\data\20180827\test.csv', 'rt', encoding='utf8')
csv_file = csv.reader(input_file)

#读取数据，返回数据列表datasList
def readData(csv_file):
    datasList=[]
    for data in csv_file:
        datasList.append(data)
    datasList.remove(datasList[0]) #去除第一行中文标识
    return datasList

def getXtime(datasList):
    Xtime=[]
    for data in datasList:
        Xtime.append(data[1].split(" ")[-1])
    return Xtime

def getYspeed(datasList):
    Yspeed=[]
    for data in datasList:
        Yspeed.append(float(data[16]))
    return Yspeed

def drawView(Xtime,Yspeed, XticksList):
    plt.plot(Xtime,Yspeed)
    plt.xticks(Xtime[::2],rotation=60,fontsize=7)
    plt.scatter(Xtime, Yspeed, marker='o', c='r')
    plt.show()

def getXticks(Xtime):
    beginTime = datetime.datetime.strptime(Xtime[0], "%H:%M:%S")
    endTime = datetime.datetime.strptime(Xtime[-1], "%H:%M:%S")
    XticksList=[]
    while beginTime < endTime:
        date_str = beginTime.strftime("%H:%M:%S")
        XticksList.append(date_str)
        beginTime += datetime.timedelta(minutes=10)
    return XticksList

if __name__ == '__main__':
    datasList = readData(csv_file)
    Xtime = getXtime(datasList)
    Yspeed = getYspeed(datasList)
    XticksList = getXticks(Xtime)
    print(XticksList)
    drawView(Xtime, Yspeed, XticksList)