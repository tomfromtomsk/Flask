##### IMPORTS #####
from typing import TypeVar, Generic


##### GLOBAL #####
T = TypeVar("T")
E = TypeVar("E")


##### CLASSES #####
class Generic_T(Generic[T]):
    def __new__(cls):
        inst = super().__new__(cls)
        inst.T = cls.__orig_bases__[0].__args__[0]
        return inst

class Generic_T_E(Generic[T, E]):
    def __new__(cls):
        inst = super().__new__(cls)
        inst.T = cls.__orig_bases__[0].__args__[0]
        inst.E = cls.__orig_bases__[0].__args__[1]
        return inst
