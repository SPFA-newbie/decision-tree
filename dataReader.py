import csv

# 读取数据
def read(file:str) -> list:
    arr=[]
    with open(file, "r", newline="") as dataCSV:
        reader=csv.DictReader(dataCSV)
        for row in reader:
            for key in list(row.keys()):
                if type(row[key])==str:
                    row[key]=row[key].strip()
                if row[key]=='?':
                    del row[key]
            arr.append(row)
    return arr

# 获取最小和最大值
def getMinMax(data:list, prop:str):
    maxV=-1e15
    minV=1e15
    for d in data:
        if prop in d:
            d[prop]=float(d[prop])
            if d[prop]>maxV: maxV=d[prop]
            if d[prop]<minV: minV=d[prop]
    return minV, maxV

# 处理连续数据
def standardNumber(data:list, prop:str, zeroVal:int, oneVal:int):
    for d in data:
        if prop in d:
            d[prop]=(int(d[prop])-zeroVal)/(oneVal-zeroVal)
    return data        

# 给予权重（用于处理有缺失值的数据）
def giveWeight(data:list, weightProp:str):
    for d in data:
        if weightProp in d:
            raise Exception("Existing Properties")
        else:
            d[weightProp]=1
    return data

if __name__=="__main__":
    d=read("data.csv")
    d=standardNumber(d, "age", 16, 80)
    # print(d)