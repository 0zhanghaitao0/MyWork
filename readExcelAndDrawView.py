import csv
import matplotlib.pyplot as plt
import time
from mpl_toolkits.mplot3d import axes3d
import numpy as np
import math

input_file = open(r'F:\data\20180827\test.csv', 'rt', encoding='utf8')
csv_file = csv.reader(input_file)
file = open(r'F:\data\320106.csv', 'rt', encoding='gbk') #读取行政区的数据
csv1 = csv.reader(file)


#读取数据，返回数据列表datasList
def readData(csv_file):
    datasList=[]
    for data in csv_file:
        datasList.append(data)
    return datasList

def readXinZhenData(csv1):
    area=[]
    for data in csv1:
        area.append(data)
    area.remove(area[0])
    return area

def getXtime(datasList):
    Xtime=[]
    for data in datasList:
        mytime=data[1].split(" ")[-1].split(":")
        h=mytime[0]
        m=mytime[1]
        s=mytime[2]
        time1 = h+m+s
        Xtime.append(int(time1))
    return Xtime

def getYspeed(datasList):
    Yspeed=[]
    Yaccelspeed=[]
    for data in datasList:
        Yspeed.append(float(data[17]))
        Yaccelspeed.append(float(data[18]))
    return Yspeed, Yaccelspeed

def drawView2D(Xtime,Yspeed, XticksList):
    plt.plot(Xtime,Yspeed)
    plt.xticks(Xtime[::6],rotation=60,fontsize=7)
    plt.scatter(Xtime, Yspeed, marker='o', c='r')
    # plt.ylim((-3,3))
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

def drawUserLine(Xlat, Ylng, XinZhenXlat, XinZhenYlng):
    fig = plt.figure(figsize=(30,30))
    ax = fig.gca(projection='3d')
    ax.set_zlim((0,1))
    figure1 = ax.plot(Xlat, Ylng, c='b')  # 用户轨迹
    figure2 = ax.plot(XinZhenXlat, XinZhenYlng, c='g')  # 鼓楼区行政区
    plt.show()


def drawView3D(Xtime, Xlat, Ylng, Zspeed, Zaccelspeed, XinZhenXlat, XinZhenYlng):
    fig = plt.figure(figsize=(30,30))
    ax = fig.gca(projection='3d')
    ax1=fig.gca()
    ax.set_title("3D_Curve")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    # figure1 = ax.plot(Xlat[::2], Ylng[::2], Xtime[::2], c='r') #速度
    ax.scatter(Xlat,Ylng,Zspeed)
    # figure2 = ax1.plot(Xlat[::2], Ylng[::2],c='green')
    figure3 = ax1.plot( XinZhenXlat, XinZhenYlng, c='b') #鼓楼区行政区
    plt.show()

def getXlat(datasList):
    Xlat=[]
    for data in datasList:
        Xlat.append(float(data[4]))
    return Xlat

def getYlng(datasList):
    Ylng=[]
    for data in datasList:
        Ylng.append(float(data[3]))
    return Ylng

def getXinZhenXlat(area):
    XinZhenXlat=[]
    for data in area:
        XinZhenXlat.append(float(data[2]))
    return XinZhenXlat

def getXinZhenYlng(area):
    XinZhenYlng=[]
    for data in area:
        XinZhenYlng.append(float(data[1]))
    return XinZhenYlng


if __name__ == '__main__':
    datasList = readData(csv_file)
    area = readXinZhenData(csv1)
    XinZhenXlat = getXinZhenXlat(area) #获取行政区纬度
    XinZhenYlng = getXinZhenYlng(area) #获取行政区经度
    Xtime = getXtime(datasList)
    Xlat = getXlat(datasList) #获取用户数据纬度
    Ylng = getYlng(datasList) #获取用户数据经度
    Zspeed, Zaccelspeed = getYspeed(datasList)
    # XticksList = getXticks(Xtime)
    # drawView2D(Xtime, Zspeed, XticksList)
    drawView3D(Xtime, Xlat, Ylng, Zspeed,Zaccelspeed, XinZhenXlat, XinZhenYlng)

    # drawUserLine(Xlat, Ylng, XinZhenXlat, XinZhenYlng)