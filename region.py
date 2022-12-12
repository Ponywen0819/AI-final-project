import numpy as np

class Region:
    def __init__(self, data: np.ndarray, x: int = 0, y: int = 0):
        self.x = x; self.y = y; self.data = data

    def __str__(self):
        return "( x: %d y: %d w: %d h: %d )" % (self.x, self.y, self.data.shape[1], self.data.shape[0])

    def get_info(self):
        return self.x, self.y, self.data.shape[1], self.data.shape[0]