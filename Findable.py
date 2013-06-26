import inspect

class Findable:
    def __init__(self):
        pass

    def find(self, attributes):
        count = 0
        for attr in attributes:
            if attr in self.__dict__.keys() and self.__dict__[attr] == attributes[attr]:
                count = count + 1
            else:
                for member in inspect.getmembers(self):
                    if member[0] == attr and inspect.ismethod(member[1]) and member[1]() == attributes[attr]:
                        count = count + 1
        return count == len(attributes)
