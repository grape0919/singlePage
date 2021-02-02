

class CompositionData:
    composition = ''
    description_list = {}

    def __init__(self, composition):
        self.composition = composition
        self.description_list = ['' for i in range(10)]

    def addDescription(self, index, description):
        self.description_list[index-1] = description

    def getDescriptionList(self):
        return self.description_list

    def getSpreadData(self):
        temp = []
        temp.append(self.composition)
        temp = temp + self.description_list
        return temp