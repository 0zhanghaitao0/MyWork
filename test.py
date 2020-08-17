import pandas as pd
import csv
import math
import datetime
import time as t
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

def changTimeFoemat(datasList): #修改时间格式为2018-8-27 00:48:01
    for data in datasList:
        newdata1 = datetime.strptime(data[1], "%Y%m%d%H%M%S")
        newdata2 = datetime.strptime(data[5], "%Y%m%d%H%M%S")
        data.pop(1)
        data.insert(1, newdata1)
        data.pop(5)
        data.insert(5, newdata2)

#去除起始基站经纬度或结束基站经纬度为0的数据
def deleteZeroData(datasList):
    deleteList=[] #存储将要删除的数据即经纬度为0的数据
    for data in datasList:
        if float(data[3]) == 0 or float(data[4]) == 0 or float(data[7]) == 0 or float(data[8]) == 0:
            deleteList.append(data)
    for data in deleteList:
        datasList.remove(data)
    return datasList

def groupByUserId(datasList): #根据用户号码为分类出不同的用户
    list1=[]
    dataGroupsList=[] #存储不同用户的信令数据
    list=[] #中间列表
    for i in range(0 , len(datasList)-1):

        if datasList[i][0] == datasList[i+1][0]:
            list.append(datasList[i])
        else:
            list.append(datasList[i])
            dataGroupsList.append(list)
            list=[]
    #添加上最后一组用户的数据
    index = datasList.index(dataGroupsList[-1][-1])
    list=[]
    for i in range(index+1, len(datasList)):
        list.append(datasList[i])
    dataGroupsList.append(list)
    # for data in dataGroupsList:
    #     for i in data:
    #         list1.append(i)
    # print(len(list1))
    return dataGroupsList

def distinguishTravel(dataGroupsList): #为每个用户区分不同的行程，并且打上每段行程的标记
    #给不同用户标识不同的行程标记
    for dataGroup in dataGroupsList:
        flag = 1
        for i in range(0, len(dataGroup)-1):
            if dataGroup[i][5] == dataGroup[i+1][1]:
                dataGroup[i].append(flag)
            else:
                dataGroup[i].append(flag)
                flag = flag+1
        if flag!=1:
            dataGroup[-1].append((flag))
        else:
            dataGroup[-1].append(flag)
    # list=[]
    # for dataGroup in dataGroupsList: #[[[不同行程数据]不同用户数据]所有数据]
    #     for data in dataGroup:
    #         list.append(data)
    #给用户继续细化分不同的行程
    allUser = []
    for dataGroup in dataGroupsList:
        user = []
        travel = []
        flag = 1
        for data in dataGroup:
            if data[10] == flag:
                travel.append(data)
            elif data[10] != flag:
                user.append(travel)
                travel = []
                flag = flag+1
                travel.append(data)
        user.append(travel) #添加每段行程的最后一次数据记录
        allUser.append(user)
    return allUser  #格式:[allUser[user[travel]]]

def removePingPong(dataGroupsList): #对不同的行程段消除乒乓效应造成的误差
    for i in range(0, 10):
        for dataGroup in dataGroupsList:
           for data in dataGroup:
               removePingPongMethod(data)
    return dataGroupsList

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

def removeDriftData(dataGroupsList): #网格化清洗掉漂移数据
    sizeLat = 0.0045487013  # 500m x 500m 的网格
    sizeLng = 0.0045487002
    for user in dataGroupsList:
        for travel in user:
            test1(travel)
            # for data in travel:
            #     if data not in list:
            #         travel.remove(data)
    return dataGroupsList

def test1(travel):
    if len(travel) > 2:
        index=1
        while(index<len(travel)-1):
            content0 = travel[index-1]
            content1 = travel[index]
            content2 = travel[index+1]
            L01 = compute_twopoint_distance(content0, content1)
            L02 = compute_twopoint_distance(content0, content2)
            L12 = compute_twopoint_distance(content1, content2)
            if L01>700 and L12>700 and L02<=700:
                travel.remove(travel[index])
            else:
                index = index+1

def grid(dataframes, lng, lat): #对每一段行程记录进行网格化
    Cm = []
    cluster = []
    cluster.append(dataframes[0])  # 第一条记录默认为起始点
    index = 0
    if len(dataframes)>1:
        while (index < len(dataframes) - 1):
            content1 = float(dataframes[index + 1][3])
            content2 = float(dataframes[index + 1][4])
            if content1 >= float(dataframes[index][3]) - lng and content1 <= float(dataframes[index][3]) + lng and content2 >= float(dataframes[index][4]) - lat and content2 <= float(dataframes[index][4]) + lat:
                cluster.append(dataframes[index + 1])
                index = index + 1
            else:
                Cm.append(cluster)
                cluster = []
                cluster.append(dataframes[index + 1])
                index = index + 1
        return parse_Cm(Cm)
    else:
        return dataframes
def parse_Cm(Cm): #对网格化的数据进行处理,处理方法：
    index=1
    length = len(Cm)
    while index<length-1:
        content0=Cm[index-1][-1]
        content01=Cm[index][0]
        content1=Cm[index][-1]
        content2=Cm[index+1][0]
        distance01 = compute_twopoint_distance(content0,content01)
        distance12=compute_twopoint_distance(content1,content2)
        distance02 = compute_twopoint_distance(content0, content2)
        if distance12>=700 and distance01>=700 and distance02<700:
            #if len(Cm[index])>= len(Cm[index+1]) and len(Cm[index]):
            Cm.remove(Cm[index])
        else:
            index=index+1
        length = len(Cm)
    cm=[]
    for content1 in Cm:
        for content2 in content1:
            cm.append(content2)
        # if len(content1)!=1:
        #     print(len(content1))
        #     cm.append(content1[0])
        #     cm.append(content1[-1])
        # else:
        #     cm.append(content1[0])
    return cm

def deleteRepeatData(dataGroupsList): #分行程去除重复的数据
    for index in range(0,10):
        for user in dataGroupsList:
            for travel in user:
                deleList=[]
                if len(travel) > 1:
                    for i in range(1, len(travel)):
                        if travel[i][3] == travel[i-1][3] and travel[i][4] == travel[i-1][4]:
                            if travel[i-1] not in deleList:
                                deleList.append(travel[i-1])
                    for data in deleList:
                        travel.remove(data)
    return dataGroupsList

def computeDistance(dataGroupsList): #计算距离
    for user in dataGroupsList:
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
    return dataGroupsList

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

def computeTimeDiff(dataGroupsList): #重新计算时间
    for user in dataGroupsList:
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
    return dataGroupsList


def computeSpeed(dataGroupsList): #计算速度
    for user in dataGroupsList:
        # T = 1.3 #T为系数1.3
        for travel in user:
            list=[]
            for data in travel:
                if float(data[11]) != 0:
                    speed = float(data[12])/float(data[11])
                    data.append(speed)
                else:
                    list.append(data)
            for info in list:
                travel.remove(info)
    return dataGroupsList

def computeSpeed1(dataGroupsList): #计算速度
    for user in dataGroupsList:
        # T = 1.3 #T为系数1.3
        for travel in user:
            list=[]
            for data in travel:
                if float(data[14]) != 0:
                    speed = float(data[15])/float(data[14])
                    data.append(speed)
                else:
                    list.append(data)
            for info in list:
                travel.remove(info)
    return dataGroupsList


def computeAccelSpeed(dataGroupsList): #计算加速度
    for user in dataGroupsList:
        for travel in user:
            if len(travel)>1: #只会计算行程段里2条以上记录的加速度
                for i in range(1,len(travel)):
                    accel = (travel[i][16] - travel[i-1][16])/travel[i-1][14]
                    travel[i-1].append(accel)
                    if i == len(travel)-1: #最后一条记录数据用倒数第二条补偿
                        accel = (travel[i][16] - travel[i - 1][16]) / travel[i - 1][14]
                        travel[i].append(accel)
    return dataGroupsList

def removeBigSpeed(dataGroupsList): #速度超过33m/s，去除
    for user in dataGroupsList:
        for travel in user:
            list=[]
            if len(travel) > 1:
                for i in range(1, len(travel)):

                    if travel[i-1][13] > 33: #阈值33m/s
                        list.append(travel[i])
                for data in list:
                    travel.remove(data)
            elif len(travel) == 1 and travel[0][13] > 33:
                travel.remove(travel[0])
    for user in dataGroupsList:
        for travel in user:
            if(len(travel)==1) and travel[0][13]>33:
                travel.remove(travel[0])
    return dataGroupsList

def removeLessTwoData(dataGroupsList): #出去行程小于2条记录的数据
    for user in dataGroupsList:
        list=[]
        for travel in user:
            if len(travel)<2:
                list.append(travel)
        for delTravel in list:
            user.remove(delTravel)
    return dataGroupsList

def test(dataGroupsList):
    list=[]
    for i in dataGroupsList:
        for j in i:
            for m in j:
                list.append(m)
    return list


def write_csv(datasList):  #向csv表写数据
    cols = ['用户号码', '开始时间', '开始基站', '开始基站经度', '开始基站纬度', '结束时间', '结束基站', '结束基站经度', '结束基站纬度', '停留时间', '行程段', '停留时间', '距离', '速度', '停留时间', '距离', '速度', '加速度']
    datas_List = pd.DataFrame(datasList)
    datas_List.columns = cols
    datas_List.to_csv(r'F:\data\20180827\14' + '.csv', index=None, encoding='utf_8_sig')

if __name__ == '__main__':
    datasList = readData(csv_file)  # 读取数据,datasList为接收的数据列表
    changTimeFoemat(datasList)  # 修改时间格式为2018-8-27 00:48
    datasList = deleteZeroData(datasList)  # 删除经纬度为0的数据
    dataGroupsList = groupByUserId(datasList)  # 根据用户号码为分类出不同的用户
    dataGroupsList = distinguishTravel(dataGroupsList)  # 为每个用户区分不同的行程，并且打上每段行程的标记
    dataGroupsList = computeTimeDiff(dataGroupsList)  # 重新计算停留时间
    dataGroupsList = computeDistance(dataGroupsList)  # 计算距离
    dataGroupsList = computeSpeed(dataGroupsList)  # 计算速度
    dataGroupsList = computeTimeDiff(dataGroupsList)  # 重新计算停留时间
    dataGroupsList = computeDistance(dataGroupsList)  # 计算距离
    dataGroupsList = computeSpeed1(dataGroupsList)  # 计算速度
    dataGroupsList = removeLessTwoData(dataGroupsList)  # 出去行程小于2条记录的数据
    dataGroupsList = computeAccelSpeed(dataGroupsList)  # 计算加速度
    list = test(dataGroupsList)
    write_csv(list)