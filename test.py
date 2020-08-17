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
    return dataGroupsList

#网格化
def grid(dataGroupsList, lng, lat, T):
    for user in dataGroupsList:
        classcluster = []
        cluster = []
        delcluster = []
        i = 0
        m = 0
        flag = 0
        while i < len(user)-1:
            if float(user[i+1][3]) < float(user[i][3]) + lng and float(user[i+1][3]) > float(user[i][3]) - lng and float(user[i+1][4]) < float(user[i][4]) + lat and float(user[i+1][4]) > float(user[i][4]) - lat:
                cluster.append(user[i+1])
                if user[i] not in cluster:
                    cluster.append(user[i])
                print("i---{}".format(i))
            #寻找T分钟内是否有点在网格范围内
            else:
                if user[i] not in cluster:
                    cluster.append(user[i])
                flag = 1
                j = i+1
                print("j---{}".format(j))
                count = 0
                while j < len(user):
                    total_seconds = (user[j][1] - user[i][1]).total_seconds()
                    if total_seconds<T:
                        if float(user[j][3]) < float(user[i][3]) + lng and float(user[j][3]) > float(user[i][3]) - lng and float(user[j][4]) < float(user[i][4]) + lat and float(user[j][4]) > float(user[i][4]) - lat:
                            #如果在T分钟内找到了
                            cluster.append(user[j])
                            for index in range(i+1+m, j): #将中间数据添加到待删除簇中
                                delcluster.append(user[index])
                            i = j
                            i = i-1 #抵消最后的i=i+1
                            break
                        else:
                            # if flag == 0: #本级未找到，将中心点向上返回一级，继续以上一级为中心点继续向下寻找
                            m = m + 1  # 记录向上返回了几级
                            i = i - 1  # 返回上一级
                            j = j - count #j 要从原来的开始
                            count = 0
                            if m > len(cluster):  # 如果返回上一级返回到数据起始 位置，那么就说明不再可能找到了，此时要讲原来的簇加入到类簇中，并开辟一条新簇
                                classcluster.append(cluster)
                                cluster = []
                                i = i + m  # 恢复原来遍历到的位置
                                m = 0
                                break
                    else:
                        classcluster.append(cluster) #如果下面的点都没有小于5分钟的，直接开辟一条新簇
                        cluster = []
                        break
                    j = j + 1
                    count = count + 1
            i=i+1
        if cluster not in classcluster:
            classcluster.append(cluster)
        for deldata in delcluster:
            user.remove(deldata) #删除中间的数据
        clusternumber = 1 #聚类编号,起始编号从1开始
        for cluster in classcluster:
            if len(cluster)>0:
                for info in cluster:
                    info.append(clusternumber)
                clusternumber = clusternumber + 1
    return dataGroupsList


def test(dataGroupsList):
    list = []
    for user in dataGroupsList:
        for info in user:
            list.append(info)
    return list

def write_csv(datasList):  # 向csv表写数据
    cols = ['用户号码', '开始时间', '开始基站', '开始基站经度', '开始基站纬度', '结束时间', '结束基站', '结束基站经度', '结束基站纬度', '停留时间', '聚类簇编号','1']
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
    dataGroupsList = grid(dataGroupsList, lng, lat, T)
    list = test(dataGroupsList)
    write_csv(list)

