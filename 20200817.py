#基于网格的聚类算法
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
        newdata1 = datetime.datetime.strptime(data[1], "%Y%m%d%H%M%S")
        newdata2 = datetime.datetime.strptime(data[5], "%Y%m%d%H%M%S")
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
                else:
                    user[i-1].pop(7)
                    user[i-1].insert(7, float(user[i][3]))
                    user[i-1].pop(8)
                    user[i-1].insert(8, float(user[i][4]))
                    i = i + 1
            if float(user[i][3]) == 0 and float(user[i][4]) == 0:
                user[i].pop(3)
                user[i].insert(3, user[i-1][7])
                user[i].pop(4)
                user[i].insert(4, user[i-1][8])
    return dataGroupsList

def test(dataGroupsList):
    list = []
    for user in dataGroupsList:
        for info in user:
            list.append(info)
    return list


def write_csv(datasList):  # 向csv表写数据
    cols = ['用户号码', '开始时间', '开始基站', '开始基站经度', '开始基站纬度', '结束时间', '结束基站', '结束基站经度', '结束基站纬度', '停留时间']
    datas_List = pd.DataFrame(datasList)
    datas_List.columns = cols
    datas_List.to_csv(r'F:\data\20180827\17' + '.csv', index=None, encoding='utf_8_sig')

if __name__ == '__main__':
    datasList = readData(csv_file) #读取数据
    datasList = changTimeFormat(datasList) #修改数据格式
    dataGroupsList = groupByUserId(datasList) #按userid进行用户分类
    dataGroupsList = recoverData(dataGroupsList) #数据补偿
    list = test(dataGroupsList)
    write_csv(list)

