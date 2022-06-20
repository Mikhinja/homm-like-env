from gym import spaces
from typing import Optional
from gym.utils import seeding

class DiscreteMasked(spaces.Discrete):
    SAMPLED:bool=False
    def __init__(self, n: int, seed = None, start: int = 0):
        #super().__init__(n, seed, start)
        super().__init__(n) # for py 3.9
        self.mask = None
    def sample(self) -> int:
        if self.__has_mask__():
            DiscreteMasked.SAMPLED = True
            return self.np_random.choice([idx for idx in range(self.n) if self.mask[idx]])
        return super().sample()
    def contains(self, x) -> bool:
        if self.__has_mask__():
            as_int = int(x)
            return self.start <= as_int < self.start + self.n and self.mask[as_int]
        return super().contains(x)
    def UpdateMask(self, mask:list[bool]):
        assert len(mask) == self.n
        self.mask = mask
    def __has_mask__(self) -> bool:
        return self.mask is not None and len(self.mask) == self.n