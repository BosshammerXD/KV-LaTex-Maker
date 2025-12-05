from itertools import count
from typing import Generic, TypeVar

from IterTools import IDGenerator


_T = TypeVar("_T")

class IDiedVal(Generic[_T]):
    __ID_GENERATOR = IDGenerator(count())
    def __init__(self, val: str) -> None:
        self.val: str = val
        self.__id: int = IDiedVal.__ID_GENERATOR.generate_id()
    
    @property
    def id(self) -> int:
        return self.__id
    
    def __del__(self) -> None:
        IDiedVal.__ID_GENERATOR.release_id(self.__id)