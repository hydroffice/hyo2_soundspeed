from abc import ABCMeta, abstractmethod


class AbstractTest(object, metaclass=ABCMeta):
    """ Common abstract data format """

    def __init__(self):
        pass

    @abstractmethod
    def test(self):
        pass


class DerivedTest(AbstractTest):

    def __init__(self):
        pass

    def test(self):
        pass


derived = DerivedTest()
print(derived)