import math
import copy

# 计算划分依据
# data          将要划分的数据集
# target        作为决策结果的属性
# prop          进行划分的属性
# weightProp    作为权重的属性
# continuous    是否是连续数据
# 连续值划分会额外返回一个划分点
class divideTools: 
    # 求信息熵
    def Ent(data:list, target:str):
        items={}
        sum=0
        for d in data:
            if d[target] not in items: items[d[target]]=0
            items[d[target]]+=1
            sum+=1
        ent=0
        for val in items.values():
            ent-=(val/sum)*math.log2(val/sum)
        return ent
    
    # 总是二分
    def __ContinuousGain(data:list, prop:str, target:str):
        dichotomyData=[]
        maxValue=-1e15
        minValue=1e15
        for d in data:
            if d[prop]>maxValue:maxValue=d[prop]
            if d[prop]<minValue:minValue=d[prop]
        middle=(maxValue+minValue)/2
        for d in data:
            td=copy.deepcopy(d)
            if td[prop]>middle: td[prop]="GT"
            else: td[prop]="LE"
            dichotomyData.append(td)
        return divideTools.Gain(dichotomyData, prop, target), middle

    # 求信息增益
    def Gain(data:list, prop:str, target:str, continuous:bool = False):
        if continuous==True:
            return divideTools.__ContinuousGain(data, prop, target)
        classification={}
        sum=len(data)
        for d in data:
            if d[prop] not in classification:
                classification[d[prop]]=[]
            classification[d[prop]].append(d)

        gain=divideTools.Ent(data, target)
        for c in classification.values():
            gain-=(len(c)/sum)*divideTools.Ent(c, target)
        return gain

    # 求有缺失值情况下的信息增益
    # result[1]     连续情况下的划分点
    def incompleteGain(data:list, prop:str, weightProp:str, target:str, continuous:bool = False):
        weightAll=0
        weightComplete=0
        completeData=[]
        for d in data:
            weightAll+=d[weightProp]
            if prop in d:
                weightComplete+=d[weightProp]
                completeData.append(d)
        
        result=divideTools.Gain(completeData, prop, target, continuous)
        if type(result)==float or type(result)==int:
            return (weightComplete/weightAll)*result
        else:
            return (weightComplete/weightAll)*result[0], result[1] 
 
    def __divideContinuousData(data:list, prop:str, weightProp:str, cpoint:float):
        if cpoint==None:
            raise Exception("cpoint lost")
        result={
            "GT":[[], 0],
            "LE":[[], 0]
        }
        sum=0
        incomplete=[]
        for d in data:
            if prop not in d:
                incomplete.append(d)
            elif d[prop]>cpoint:
                result["GT"][0].append(d)
                result["GT"][1]+=1.0
                sum+=1
            else:
                result["LE"][0].append(d)
                result["LE"][1]+=1.0
                sum+=1
        result["GT"][1]/=sum
        result["LE"][1]/=sum
        for d in incomplete:
            dGT=copy.deepcopy(d)
            dGT[weightProp]*=result["GT"][1]
            result["GT"][0].append(dGT)
            dLE=copy.deepcopy(d)
            dLE[weightProp]*=result["LE"][1]
            result["LE"][0].append(dLE)
        return result
    
    # 拆分数据集
    # 提供切分点即表示拆分依据为连续值    
    def divideData(data:list, prop:str, weightProp:str, cpoint:float = None):
        if cpoint!=None:
            return divideTools.__divideContinuousData(data, prop, weightProp, cpoint)
        result={}
        sum=0
        incomplete=[]
        for d in data:
            if prop not in d:
                incomplete.append(d)
            else:
                if d[prop] not in result:
                    result[d[prop]]=[[], 0]
                result[d[prop]][0].append(d)
                result[d[prop]][1]+=1.0
                sum+=1.0
        for key in result.keys():
            tw=result[key][1]/sum
            tp=result[key][0]
            for d in incomplete:
                td=copy.deepcopy(d)
                td[weightProp]*=tw
                tp.append(td)
            result[key][1]=tw
            result[key][0]=tp
        return result
        
    # 查询当前占比最高的结果  
    def findBest(data:list, target:str):
        targetSum={}
        for d in data:
            if d[target] not in targetSum:
                targetSum[d[target]]=0
            targetSum[d[target]]+=1
        maxVal=0
        best=""
        for result, value in targetSum.items():
            if value>maxVal:
                maxVal=value
                best=result
        return best


# 终止条件检测：prop相同
def stopTest(data:list, target:str, continuousProp:list, discretenessProp:list) -> tuple:
    for prop in discretenessProp:
        i=0
        while i<len(data) and prop not in data[i]: i+=1
        if i==len(data): continue
        value=data[i][prop]
        for d in data:
            if prop in d and d[prop]!=value:
                return (False, None)
    for prop in continuousProp:
        i=0
        while i<len(data) and prop[0] not in data[i]: i+=1
        if i==len(data): continue
        maxVal=data[i][prop[0]]
        minVal=data[i][prop[0]]
        for d in data:
            if prop[0] in d:
                if d[prop[0]]>maxVal: maxVal=d[prop[0]]
                if d[prop[0]]<minVal: minVal=d[prop[0]]
                # prop[1]   最大容差
                if maxVal-minVal>prop[1]:
                    return (False, None)
    
    targetSum={}
    for d in data:
        if d[target] not in targetSum:
            targetSum[d[target]]=0
        targetSum[d[target]]+=1
    
    maxVal=0
    best=""
    for result, value in targetSum.items():
        if value>maxVal:
            maxVal=value
            best=result
    return (True, best)

# 构建决策树
# data              将要划分的数据集
# target            作为决策结果的属性
# weightProp        作为权重的属性
# continuousProp    (连续的属性, 属性容差)
# discretenessProp  离散的属性
# minGain           最小增益
import treeNode
def treeMaker(data:list, target:str, weightProp:str, continuousProp:list, discretenessProp:list, minGain:float=1e-15) -> treeNode.TreeNode:
    # 终止条件：target全部相同，此时信息熵为0
    if divideTools.Ent(data, target)<1e-15:
        return treeNode.TreeNode(result=data[0][target])
    
    # 终止条件：prop全部相同
    (canStop, stopResult)=stopTest(data, target, continuousProp, discretenessProp)
    if canStop==True:
        return treeNode.TreeNode(result=stopResult)

    # 划分
    stepProp={
        "prop":str,
        "continuous":bool,
        "cpoint":float,
        "value":float
    }
    stepProp["value"]=0
    for prop in continuousProp:
        gain, cpoint=divideTools.incompleteGain(data, prop[0], weightProp, target, True)
        if gain>stepProp["value"]:
            stepProp["prop"]=prop[0]
            stepProp["continuous"]=True
            stepProp["cpoint"]=cpoint
            stepProp["value"]=gain
    for prop in discretenessProp:
        gain=divideTools.incompleteGain(data, prop, weightProp, target)
        if gain>stepProp["value"]:
            stepProp["prop"]=prop
            stepProp["continuous"]=False
            stepProp["cpoint"]=None
            stepProp["value"]=gain
    
    # 增益过小：放弃划分(终止)
    if stepProp["value"]<minGain:
        return treeNode.TreeNode(result=divideTools.findBest(data, target))

    divide=None
    node=None
    default=divideTools.findBest(data, target)# 用于处理分支缺失的情况(直接终止)
    if stepProp["continuous"]==True:
        node=treeNode.TreeNode(prop=stepProp["prop"], continuous=True, cutterPoint=stepProp["cpoint"], default=default)
        divide=divideTools.divideData(data, stepProp["prop"], weightProp, stepProp["cpoint"])
    else:
        node=treeNode.TreeNode(prop=stepProp["prop"], continuous=False, default=default)
        divide=divideTools.divideData(data, stepProp["prop"], weightProp)

    for key, d in divide.items():
        node.append(key, treeMaker(d[0], target, weightProp, continuousProp, discretenessProp), d[1])
    return node
        
# 输出决策树
# node      当前节点
# dep       节点深度
# inChild   来自上层的信息
# output    输出文件(为None表示标准输出)
def printTree(node:treeNode.TreeNode, dep:int=0, inChild:str=None, output=None):
    nowNode=""
    for i in range(0, dep):
        nowNode+="\t"
    if inChild!=None:
        nowNode+=("from=" + inChild)
    else:
        nowNode+="root"
    # info = cprop | result
    isLeaf, info, cpoint=node.returnNode()
    next={}
    if isLeaf==False:
        nowNode+=(", prop=" + str(info))
        if cpoint!=None:
            nowNode+=(", point=" + str(cpoint))
        next=node.allChild()
    else:
        nowNode+=(", Leaf, result="+str(info))
    if output==None:
        print(nowNode)
    else:
        output.write(nowNode+"\n")
    for f, n in next.items():
        printTree(n[0], dep+1, f+", weight="+str(n[1]), output)
    return None

if __name__=="__main__":
    import dataReader
    data=dataReader.read("data.csv")
    data=dataReader.standardNumber(data, "age", 16, 80)
    data=dataReader.standardNumber(data, "fnlwgt", 0, 100000)
    data=dataReader.giveWeight(data, "w")
    # print(divideTools.incompleteGain(data, "age", "w", "class", True))
    # print(divideTools.incompleteGain(data, "education", "w", "class"))
    root:treeNode.TreeNode = treeMaker(data, "class", "w", [("age", 0.1), ("fnlwgt", 100)], ["sex", "education"])
    with open("tree.txt", mode="w", encoding="utf-8") as f:
        printTree(root, output=f)