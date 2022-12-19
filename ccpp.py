import cv2
import numpy as np
import math
from rolling import rolling
SIZE = 10



class CCPP:
    def __init__(self, start: tuple, map: np.ndarray):
        self.map = map
        self.start = start
        # 用於存放全地圖的cost
        self.cost = np.zeros(map.shape[:2], dtype=int)

        # 初始化資料
        self.enlarge_map()      # 放大資料

    @staticmethod
    def get_distance(x_1, y_1, x_2, y_2):
        return ((x_1 - x_2) ** 2 + (y_1 - y_2) ** 2) ** 0.5

    def enlarge_map(self):
        rolling_sign = rolling()
        # 用於存放障礙物放大後的地圖
        res = np.copy(self.map)

        # 遍歷全部的節點
        for y in range(self.map.shape[0]):
            for x in range(self.map.shape[1]):
                next(rolling_sign)
                if self.map[y, x] == 0:
                    continue
                if (self.map[y, x] == 2) or (self.map[y, x] == 3):
                    res[y, x] = 0
                    continue
                # 檢查是否是障礙物邊緣
                is_edge = False
                for i, j in [(0, 1), (1, 0), (-1, 0), (0, -1)]:
                    try:
                        if int(self.map[y + j, x + i]) == 0:
                            is_edge = True
                    except:
                        pass
                if not is_edge:
                    continue

                # 在黑色的周圍 也就是障礙物附近擴張
                for i in range(x - SIZE, x + SIZE + 1):
                    for j in range(y - SIZE, y + SIZE + 1):
                        if self.get_distance(x + 0.5, y + 0.5, i, j) < SIZE + 0.5:
                            try:
                                res[j, i] = 1
                            except:
                                pass
        # 地圖邊緣膨脹
        for y in range(-1, self.map.shape[0] + 1):
            for i in range(-SIZE, SIZE + 1):
                for j in range(-SIZE, SIZE + 1):
                    if self.get_distance(-0.5, y + 0.5, i - 1, j + y) < SIZE + 0.5:
                        try:
                            res[j + y, i - 1] = 1
                        except:
                            pass
        for x in range(-1, self.map.shape[1] + 1):
            for i in range(-SIZE, SIZE + 1):
                for j in range(-SIZE, SIZE + 1):
                    if self.get_distance(x + 0.5, -0.5, i + x, j - 1) < SIZE + 0.5:
                        try:
                            res[j - 1, i + x] = 1
                        except:
                            pass

        self.map = res

    def get_cost_map(self):

        for x in range(self.map[])

