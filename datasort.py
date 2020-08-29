import csv
import requests
import json

input_file = open(r'D:\final.csv', 'rt', encoding='utf8')
csv_file = csv.reader(input_file)

#读取数据，返回数据列表datasList
def readData(csv_file):
    datasList=[]
    for data in csv_file:
        datasList.append(data)
    datasList.remove(datasList[0]) #去除第一行中文标识
    return datasList

def timeSort(dataList):
    list0_6 = []
    list6_9 = []
    list9_12 = []
    list12_15 = []
    list15_18 = []
    list18_21 = []
    list21_24 = []
    for data in dataList:
        # print(data[1].split(" ")[-1])
        Time = data[1].split(" ")[-1]
        if Time >= '00:00:00' and Time<'06:00:00':
            list0_6.append(data)
        elif Time>='06:00:00' and Time<'09:00:00':
            list6_9.append(data)
        elif Time>='09:00:00' and Time<'12:00:00':
            list9_12.append(data)
        elif Time>='12:00:00' and Time<'15:00:00':
            list12_15.append(data)
        elif Time>='15:00:00' and Time<'18:00:00':
            list15_18.append(data)
        elif Time>='18:00:00' and Time<'21:00:00':
            list18_21.append(data)
        else:
            list21_24.append(data)
    return list0_6, list6_9, list9_12, list12_15, list15_18, list18_21, list21_24

def transform(data1,data2):
    url = 'http://api.map.baidu.com/geoconv/v1/?coords={},{}&from=1&to=5&ak=0FuoX30MFf7YMrdS5Wi9GGAcHBblKDuu'.format(data1, data2)
    req = requests.get(url)
    text = req.text
    text = json.loads(text)
    print(text)
    x = text['result'][0]['x']
    y = text['result'][0]['y']
    return x, y
def traffic(list):
    list1 = [] #label=1 步行
    list2 = [] #label=2 公交车
    list3 = [] #label=3 小汽车
    list4 = [] #label=4 地铁

    for data in list:
        listx = []
        # if data[9] == '1':
        #     x, y = transform(float(data[3]), float(data[4]))
        #     listx.append(y)
        #     listx.append(x)
        #     list1.append(listx)
        # if data[9] == '2':
        #     x, y = transform(float(data[3]), float(data[4]))
        #     listx.append(y)
        #     listx.append(x)
        #     list2.append(listx)
        # if data[9] == '3':
        #     x, y = transform(float(data[3]), float(data[4]))
        #     listx.append(y)
        #     listx.append(x)
        #     list3.append(listx)
        if data[9] == '4':
            x, y = transform(float(data[3]), float(data[4]))
            listx.append(y)
            listx.append(x)
            list4.append(listx)
    print(list1)
    print("***********************************")
    print(list2)
    print("***********************************")
    print(list3)
    print("***********************************")
    print(list4)

if __name__ == '__main__':
    dataList = readData(csv_file)
    list0_6, list6_9, list9_12, list12_15, list15_18, list18_21, list21_24 = timeSort(dataList)
    traffic(list21_24)