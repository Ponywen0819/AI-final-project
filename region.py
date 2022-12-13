import numpy as np

class Region:
    def __init__(self, map: np.ndarray, x: int = 0, y: int = 0):
        self.x = x
        self.y = y
        self.map = map
        self.nearby = []

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.map.shape == other.map.shape

    def __str__(self):
        return "( x: %d y: %d w: %d h: %d )" % (self.x, self.y, self.map.shape[1], self.map.shape[0])

    def get_info(self):
        return self.x, self.y, self.map.shape[1], self.map.shape[0]

    def set_near(self, r):
        self.nearby.append(r)

    def del_near(self, r):
        index = self.nearby.index(r)
        self.nearby.pop(index)

    def add_near(self, r):
        if r not in self.nearby:
            self.nearby.append(r)

    def del_near(self, r):
        if r in self.nearby:
            self.nearby.remove(r)


