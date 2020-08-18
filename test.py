import pandas as pd
import csv
import math
import datetime
from datetime import datetime

input_file = open(r'F:\data\20180827\part-00000.csv', 'rt', encoding='utf8')
csv_file = csv.reader(input_file)

#读取数据，返回数据列表datasList
def readData(csv_file):
    datasList=[]
    for data in csv_file:
        datasList.append(data)
    datasList.remove(datasList[0]) #去除第一行中文标识
    return datasList

def changTimeFormat(datasList): #修改时间格式为2018-8-27 00:48:01
    for data in datasList:
        newdata1 = datetime.strptime(data[1], "%Y%m%d%H%M%S")
        newdata2 = datetime.strptime(data[5], "%Y%m%d%H%M%S")
        data.pop(1)
        data.insert(1, newdata1)
        data.pop(5)
        data.insert(5, newdata2)
    return datasList

def groupByUserId(datasList):  # 根据用户号码为分类出不同的用户
    list1 = []
    dataGroupsList = []  # 存储不同用户的信令数据
    list = []  # 中间列表
    for i in range(0, len(datasList) - 1):

        if datasList[i][0] == datasList[i + 1][0]:
            list.append(datasList[i])
        else:
            list.append(datasList[i])
            dataGroupsList.append(list)
            list = []
    # 添加上最后一组用户的数据
    index = datasList.index(dataGroupsList[-1][-1])
    list = []
    for i in range(index + 1, len(datasList)):
        list.append(datasList[i])
    dataGroupsList.append(list)
    # for data in dataGroupsList:
    #     for i in data:
    #         list1.append(i)
    # print(len(list1))
    return dataGroupsList

#对一些缺失数据进行就近补偿，尽可能的恢复数据的完整性与时间上的连续性
def recoverData(dataGroupsList):
    for user in dataGroupsList:
        list = []
        for i in range(0, len(user)): #去除起始时刻的异常数据
            if float(user[i][3]) == 0 and float(user[i][4]) == 0:
                list.append(user[i])
            else:
                break
        for data in list:
            user.remove(data)
        i = 1
        while i < len(user)-1:
            if float(user[i-1][7]) == 0 and float(user[i-1][8]) == 0:
                if float(user[i][3]) == 0 and float(user[i][4]) == 0:
                    user[i-1].pop(5)
                    user[i-1].insert(5, user[i][5]) #时间
                    user[i-1].pop(7)
                    user[i-1].insert(7, float(user[i][7]))
                    user[i-1].pop(8)
                    user[i-1].insert(8, float(user[i][8]))
                    user.remove(user[i])
                    i = i - 1
                else:
                    user[i-1].pop(7)
                    user[i-1].insert(7, float(user[i][3]))
                    user[i-1].pop(8)
                    user[i-1].insert(8, float(user[i][4]))

            if float(user[i][3]) == 0 and float(user[i][4]) == 0:
                user[i].pop(3)
                user[i].insert(3, user[i-1][7])
                user[i].pop(4)
                user[i].insert(4, user[i-1][8])
            i = i+1
    for user in dataGroupsList:
        i = 0
        while i < len(user)-1:
            if float(user[i][9])==0:
                user.remove(user[i+1])
            i=i+1

    return dataGroupsList

#网格化
def grid(dataGroupsList, lng, lat):
    everyuserclasscluster = []
    for user in dataGroupsList:
        classcluster = []
        cluster = []
        i = 0
        if len(user)<2 and len(user)>0: #如果用户只有一条记录
            cluster.append(user[0])
        while i < len(user)-1:
            if user[i] not in cluster: #默认第一条记录为起始记录
                cluster.append(user[i])
            if float(user[i+1][3]) < float(user[i][3]) + lng and float(user[i+1][3]) > float(user[i][3]) - lng and float(user[i+1][4]) < float(user[i][4]) + lat and float(user[i+1][4]) > float(user[i][4]) - lat:
                #在以上一点为中心的网格范围内则加入簇
                cluster.append(user[i+1])
            else:
               #如果不在以上一点为中心的网格范围内，则重新开辟一条新簇
                classcluster.append(cluster)
                cluster=[]
            i=i+1
            if i==len(user)-1 and user[i] not in cluster:
                cluster.append(user[i])
        if cluster not in classcluster:
            classcluster.append(cluster) #将最后一个簇保存到类簇
        everyuserclasscluster.append(classcluster) #用于保存每个用户的类聚类[每个用户的类聚类[聚类[数据]]]
        clusternumber = 1 #聚类编号,起始编号从1开始
        for cluster in classcluster: #给每个聚类一个编号，便于分析
            if len(cluster)>0:
                for info in cluster:
                    info.append(clusternumber)
                clusternumber = clusternumber + 1

    #计算用户相邻聚类之间的距离与速度，判断是否有聚类为漂移数据或者局部离群点
    for userclasscluster in everyuserclasscluster:
        if len(userclasscluster)>2:
            i=1
            while i < len(userclasscluster)-1:
                L01 = compute_twopoint_distance(userclasscluster[i-1][-1], userclasscluster[i][0])
                L12 = compute_twopoint_distance(userclasscluster[i][-1], userclasscluster[i+1][0])
                L02 = compute_twopoint_distance(userclasscluster[i-1][-1], userclasscluster[i+1][0])
                T01 = (userclasscluster[i-1][-1][1] - userclasscluster[i][0][1]).total_seconds()
                T12 = (userclasscluster[i][-1][1] - userclasscluster[i+1][0][1]).total_seconds()
                T02 = (userclasscluster[i-1][-1][1] - userclasscluster[i+1][0][1]).total_seconds()
                Speed01 = abs(L01/T01)
                Speed12 = abs(L01/T01)
                Speed02 = abs(L02/T02)
                if Speed01>34 and  Speed12>34 and  Speed02<34:
                    userclasscluster.remove(userclasscluster[i])
                i=i+1
    return everyuserclasscluster

def deleteRepeatData(everyuserclasscluster): #分行程去除重复的数据
    for index in range(0,10):
        for user in everyuserclasscluster:
            for travel in user:
                deleList=[]
                if len(travel) > 1:
                    for i in range(1, len(travel)):
                        if travel[i][3] == travel[i-1][3] and travel[i][4] == travel[i-1][4]:
                            if travel[i-1] not in deleList:
                                deleList.append(travel[i-1])
                    for data in deleList:
                        travel.remove(data)
    return everyuserclasscluster

def compute_twopoint_distance(content1, content2): #计算两点(两条数据)之间的距离，content1和content2是每一行的记录
    JA = float(content1[3]) / 180 * math.pi
    WA = float(content1[4]) / 180 * math.pi
    JB = float(content2[3]) / 180 * math.pi
    WB = float(content2[4]) / 180 * math.pi
    L = 2 * 6378137 * math.asin(
        math.sqrt(
            math.pow(math.sin((WA - WB) / 2), 2) + math.cos(WA) * math.cos(WB) * math.pow(
                math.sin((JA - JB) / 2), 2))
    )
    return L

def removePingPong(everyuserclasscluster): #对不同的簇，消除乒乓效应造成的误差
    for i in range(0, 10):
        for userclasscluster in everyuserclasscluster:
           for classcluster in userclasscluster:
                   removePingPongMethod(classcluster)
    return everyuserclasscluster

def removePingPongMethod(data): #消除乒乓效应造成误差的方法
    if len(data)>2:
        deleteList=[]
        for i in range(2, len(data)):
            if float(data[i][3]) == float(data[i-2][3]) and float(data[i][4]) == float(data[i-2][4]) and int(data[i-1][9]) < (5*60):
                if data[i-1] not in deleteList:
                    deleteList.append(data[i-1])
                if data[i-1] not in deleteList:
                    deleteList.append(data[i-2])
        for deldata in deleteList:
            data.remove(deldata)

def test(dataGroupsList):
    list = []
    for user in dataGroupsList:
        for info in user:
            for data in info:
                list.append(data)
    return list

def computeDistance(everyuserclasscluster): #计算距离
    for user in everyuserclasscluster:
        for travel in user:
            if len(travel)>1:
                for i in range(1, len(travel)):
                    L = compute_twopoint_distance(travel[i-1], travel[i])
                    travel[i-1].append(L)
                    if i == len(travel)-1:  #最后一条记录数据用倒数第二条补偿
                        L = compute_twopoint_distance(travel[i - 1], travel[i])
                        # L = computeDataDistance(travel[i])
                        travel[i].append(L)
            elif len(travel)==1:
                L = computeDataDistance(travel[0])
                travel[0].append(L)
            else:
                pass
    return everyuserclasscluster

def computeDataDistance(data): #计算一条数据起始位置与结束位置之间的距离
    JA = float(data[3]) / 180 * math.pi
    WA = float(data[4]) / 180 * math.pi
    JB = float(data[7]) / 180 * math.pi
    WB = float(data[8]) / 180 * math.pi
    L = 2 * 6378137 * math.asin(
        math.sqrt(
            math.pow(math.sin((WA - WB) / 2), 2) + math.cos(WA) * math.cos(WB) * math.pow(
                math.sin((JA - JB) / 2), 2))
    )
    return L

def computeTimeDiff(everyuserclasscluster): #重新计算时间
    for user in everyuserclasscluster:
        for travel in user:
            if len(travel) > 1:
                for i in range(1, len(travel)):
                    total_seconds = (travel[i][1] - travel[i-1][1]).total_seconds()
                    travel[i-1].append(total_seconds)
                    if i == len(travel)-1:  #最后一条记录数据用倒数第二条补偿
                        total_seconds = (travel[i][1] - travel[i - 1][1]).total_seconds()
                        travel[i].append(total_seconds)
            elif len(travel)==1:
                travel[0].append(travel[0][9])
            else:
                pass
    return everyuserclasscluster

def computeSpeed(everyuserclasscluster): #计算速度
    for user in everyuserclasscluster:
        # T = 1.3 #T为系数1.3
        for travel in user:
            list=[]
            for data in travel:
                if float(data[12]) != 0:
                    speed = float(data[11])/float(data[12])
                    data.append(speed)
                else:
                    list.append(data)
            for info in list:
                travel.remove(info)
    return everyuserclasscluster

def removeBigSpeed(everyuserclasscluster): #速度超过33m/s，去除
    for user in everyuserclasscluster:
        for travel in user:
            list=[]
            for data in travel:
                if data[13]>84:
                    list.append(data)
            for data in list:
                travel.remove(data)
    return everyuserclasscluster

def computeSpeed1(everyuserclasscluster): #再次计算速度
    for user in everyuserclasscluster:
        # T = 1.3 #T为系数1.3
        for travel in user:
            list=[]
            for data in travel:
                if float(data[15]) != 0:
                    speed = float(data[14])/float(data[15])
                    data.append(speed)
                else:
                    list.append(data)
            for info in list:
                travel.remove(info)
    return everyuserclasscluster

def computeAccelSpeed(everyuserclasscluster): #计算加速度
    for user in everyuserclasscluster:
        for travel in user:
            if len(travel)>1: #只会计算行程段里2条以上记录的加速度
                for i in range(1,len(travel)):
                    accel = (travel[i][-1] - travel[i-1][-1])/travel[i-1][-2]
                    travel[i-1].append(accel)
                    if i == len(travel)-1: #最后一条记录数据用倒数第二条补偿
                        accel = (travel[i][-1] - travel[i - 1][-1]) / travel[i - 1][-2]
                        travel[i].append(accel)
    return everyuserclasscluster

def write_csv(datasList):  # 向csv表写数据
    cols = ['用户号码', '开始时间', '开始基站', '开始基站经度', '开始基站纬度', '结束时间', '结束基站', '结束基站经度', '结束基站纬度', '停留时间', '聚类簇编号','距离','时间','速度','加速度','距离','时间','速度']
    datas_List = pd.DataFrame(datasList)
    datas_List.columns = cols
    datas_List.to_csv(r'F:\data\20180827\17' + '.csv', index=None, encoding='utf_8_sig')

if __name__ == '__main__':
    lng = 0.0045487002
    lat = 0.0045487013
    T = 5*60
    datasList = readData(csv_file) #读取数据
    datasList = changTimeFormat(datasList) #修改数据格式
    dataGroupsList = groupByUserId(datasList) #按userid进行用户分类
    dataGroupsList = recoverData(dataGroupsList) #数据补偿
    everyuserclasscluster = grid(dataGroupsList, lng, lat) #网格法去除漂移[[[]]]
    everyuserclasscluster = removePingPong(everyuserclasscluster)
    everyuserclasscluster = deleteRepeatData(everyuserclasscluster)
    everyuserclasscluster = computeDistance(everyuserclasscluster)
    everyuserclasscluster = computeTimeDiff(everyuserclasscluster)
    everyuserclasscluster = computeSpeed(everyuserclasscluster)
    everyuserclasscluster = computeAccelSpeed(everyuserclasscluster)
    everyuserclasscluster = removeBigSpeed(everyuserclasscluster)
    everyuserclasscluster = computeDistance(everyuserclasscluster)
    everyuserclasscluster = computeTimeDiff(everyuserclasscluster)
    everyuserclasscluster = computeSpeed1(everyuserclasscluster)
    list = test(everyuserclasscluster)
    write_csv(list)

