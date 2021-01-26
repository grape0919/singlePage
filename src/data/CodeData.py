

class CodeData:
    code = 0
    composition_list = ['' for i in range(10)]
    
    def __init__(self, code):
        self.code = code
        self.composition_list = ['' for i in range(10)]

    def addComposition(self, index, composition):
        self.composition_list[index-1] = composition

    def getCompositionList(self):
        return self.composition_list

    def getSpreadData(self):
        temp = []
        temp.append(self.code)
        temp = temp + self.composition_list
        return temp
