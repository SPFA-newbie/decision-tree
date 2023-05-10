import treeNode
import csv

# 使用决策树的一个节点对data进行预测
# data      将要进行预测的数据
# node      决策树节点
# target    预测结果的属性名
def decisionData(data:dict, node:treeNode.TreeNode) -> dict:
    # print(node.returnNode())
    isLeaf, info=node.check(data)
    if isLeaf==True:
        return {info:1}
    else:
        result={}
        for (child, weight) in info:
            subResult=decisionData(data, child)
            for r in subResult.keys():
                if r in result:
                    result[r]+=subResult[r]*weight
                else: result[r]=subResult[r]*weight
    return result

# 使用决策树并给出结果
# 结果：(实际结果，预测结果，预测概率)
def checkData(data:dict, root:treeNode.TreeNode, target:str):
    result=decisionData(data, root)
    best=0
    bestKey=None
    for key, value in result.items():
        if value>best:
            best=value
            bestKey=key
    return (data[target], bestKey, best)

# 对一组数据进行预测
# targetList    可能的预测结果
# save          保存在文件中/直接输出
# originalSave  保存在文件中/不保存
def forcast(data:list, root:treeNode.TreeNode, target:str, targetList:list, save=None, originalSave=None):
    # 原始数据
    result=[]
    # 混淆矩阵[real][forcast]
    confusion={}
    for rt in targetList:
        confusion[rt]={}
        for ft in targetList:
            confusion[rt][ft]=0
    for d in data:
        (real, forcast, frate)=checkData(d, root, target)
        if real not in confusion:
            raise Exception("Unknow result in real: "+str(real))
        if forcast not in confusion[real]:
            raise Exception("Unknow result in forcast: "+str(forcast))
        confusion[real][forcast]+=1
        if originalSave!=None:
            result.append((real, forcast, frate))    

    # 输出
    if save==None:
        print(confusion)
    else:
        outList=[["_FORCAST_"]]
        for t in targetList:
            outList[0].append(t)
            row=[t]
            for i in range(0, len(targetList)):
                row.append(0)
            outList.append(row)
        for realK, value in confusion.items():
            realPos=0
            for i in range(0, len(outList[0])):
                if outList[0][i]==realK:
                    realPos=i
            for forcastK, val in value.items():
                forcastPos=0
                for i in range(0, len(outList)):
                    if outList[i][0]==forcastK:
                        forcastPos=i
                outList[forcastPos][realPos]=val
        cf=csv.writer(save)
        cf.writerows(outList)
    if originalSave!=None:
        for r in result:
            originalSave.write(str(r)+"\n")

if __name__=="__main__":
    import dataReader
    import treeMaker
    print("build tree...")
    data=dataReader.read("data.csv")
    data=dataReader.standardNumber(data, "age", 16, 80)
    data=dataReader.standardNumber(data, "fnlwgt", 0, 100000)
    data=dataReader.giveWeight(data, "w")
    root:treeNode.TreeNode = treeMaker.treeMaker(data, "class", "w", [("age", 0.1), ("fnlwgt", 100)], ["sex", "education"])
    with open("tree.txt", mode="w", encoding="utf-8") as f:
        treeMaker.printTree(root, output=f)
    
    print("test...")
    tdata=dataReader.read("test.csv")
    tdata=dataReader.standardNumber(tdata, "age", 16, 80)
    tdata=dataReader.standardNumber(tdata, "fnlwgt", 0, 100000)
    tdata=dataReader.giveWeight(tdata, "w")
    with open("forcast.csv", mode="w", encoding="utf-8") as ff:
        with open("fresult.txt", mode="w", encoding="utf-8") as rf:
            forcast(tdata, root, "class", ["<=50K", ">50K"], ff, rf)