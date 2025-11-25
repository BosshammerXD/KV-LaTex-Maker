from abc import abstractmethod
from .KVDrawable import KVDrawable
from .KVGrid import KVGrid


class KVDrawableFromGrid(KVDrawable):
    @abstractmethod
    def draw(self, kv_grid: KVGrid):
        pass