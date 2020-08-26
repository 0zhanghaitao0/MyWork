import pandas as pd
import csv
import requests
import json

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
        x , y = transform(data[3], data[4])
        list.append(y)
        list.append(x)
        pointList.append(list)
    return pointList

def transform(data1,data2):
    url = 'http://api.map.baidu.com/geoconv/v1/?coords={},{}&from=1&to=5&ak=vKHOVd6Gd0ZECdBgwuOcSCaTvX67bD3G'.format(data1,data2)
    req = requests.get(url)
    text = req.text
    text = json.loads(text)
    x = text['result'][0]['x']
    y = text['result'][0]['y']
    return x, y

def format(datasList): #按固定的格式输出，目的是方便使用JSapi 打点和标注
    list=[]
    for content in datasList:
        #print(content)
        x, y = transform(content[3], content[4])
        str = "new BMapGL.Point({},{}),".format(x, y)
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

