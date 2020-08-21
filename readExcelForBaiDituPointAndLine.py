import pandas as pd
import csv

input_file = open(r'F:\data\20180827\test.csv', 'rt', encoding='utf8')
csv_file = csv.reader(input_file)

#读取数据，返回数据列表datasList
def readData(csv_file):
    datasList=[]
    for data in csv_file:
        datasList.append(data)
    return datasList

def formatPoint(datasList):
    list=[]
    pointList = []
    for data in datasList:
        list=[]
        list.append(data[4])
        list.append(data[3])
        pointList.append(list)
    return pointList
def format(datasList): #按固定的格式输出，目的是方便使用JSapi 打点和标注
    list=[]
    for content in datasList:
        #print(content)
        str = "new BMapGL.Point({},{}),".format(content[3], content[4])
        #print("new BMapGL.Point({},{}),".format(content[1],content[0]))
        list.append(str)
    return list

if __name__ == '__main__':
    datasList = readData(csv_file)
    pointList = formatPoint(datasList)
    print(pointList)
    list = format(datasList)
    for data in list:
        print(data)

