import copy

class TreeNode:
    # child={"propvalue":[childNode, weight]}
    __child:dict
    __checkProp:str
    __cutter:float

    __result=None
    __default=None

    # 会返回将要被分配的子节点
    # 返回值：bool(是否是结果), (结果) 或 (TreeNode(子节点), weight(权重))
    check=None
    # 叶节点
    def __resultNode(self, data:dict):
        return True, self.__result
    # 离散
    def __discreteness(self, data:dict):
        # 属性缺失
        if self.__checkProp not in data:
            ret=[]
            for val in self.__child.values():
                ret.append((val[0], val[1]))
            return False, ret
        # 分支缺失
        if data[self.__checkProp] not in self.__child:
            return True, self.__default
        return False, [(self.__child[data[self.__checkProp]][0], 1)]
    # 连续
    def __continuous(self, data:dict):
        if self.__checkProp not in data:
            ret=[]
            for val in self.__child.values():
                ret.append((val[0], val[1]))
            return False, ret
        if data[self.__checkProp]>self.__cutter:
            return False, [(self.__child["GT"][0], 1)]
        else:
            return False, [(self.__child["LE"][0], 1)]
    # 获取全部子节点，通常用于属性缺失的情况
    def allChild(self):
        return self.__child

    # 添加子节点
    def append(self, childKey:str, child, weight:float) -> None:
        self.__child[childKey]=[]
        self.__child[childKey].append(copy.deepcopy(child))
        self.__child[childKey].append(weight)
    # def setGT(self, child, weight:float) -> None:
    #     self.__child["GT"][0]=child
    #     self.__child["GT"][1]=weight
    # def setLE(self, child, weight:float) -> None:
    #     self.__child["LE"][0]=child
    #     self.__child["LE"][1]=weight

    def returnNode(self):
        if self.__result!=None:
            return True, self.__result, None
        return False, self.__checkProp, self.__cutter

    def __init__(self, prop:str = None, continuous:bool = None, cutterPoint:float = None, result = None, default = None) -> None:
        self.__checkProp=prop
        self.__cutter=cutterPoint
        self.__result=result
        self.__default=default

        if continuous==True: 
            self.check=self.__continuous
            self.__child={
                "GT":[None, 0],
                "LE":[None, 0]
            }
        elif continuous==False: 
            self.check=self.__discreteness
            self.__child={}
        else: 
            self.check=self.__resultNode
            self.__child=None
