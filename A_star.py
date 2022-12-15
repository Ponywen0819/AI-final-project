import numpy as np
import cv2
import os
from rolling import rolling


SIZE = 1

class Astar:
    def __init__(self, start: tuple, end: tuple, map: np.ndarray, file: str):
        self.start = start
        self.end = end
        self.map = map
        self.path = []
        self.file = file

        # 用來記錄待估計的地點
        self.open_set = []
        # 用來紀錄已估計過的地點
        self.close_set = [[0 for i in range(map.shape[0])] for j in range(map.shape[1])]
        # 用來記錄真實距離
        self.cost_set = [[0 for i in range(map.shape[0])] for j in range(map.shape[1])]
        # 用來記錄角度
        self.come = [[(0, 0) for i in range(map.shape[0])] for j in range(map.shape[1])]

    def setting(self, regions: list):
        self.close_set = [[1 for i in range(self.map.shape[0])] for j in range(self.map.shape[1])]
        for i in regions:
            for x in range(i[2]):
                for y in range(i[3]):
                    self.close_set[i[1] + y][i[0] + x] = 0
    def get_h(self, location: tuple)->float:
        """
        用來取得到終點的直線距離
        :param location: 估計之位置
        :return: 到終點之位置
        """
        temp_x = (location[0] - self.end[0]) ** 2
        temp_y = (location[1] - self.end[1]) ** 2
        return (temp_y + temp_x) ** 0.5

    def get_min(self):
        """
        取得open_set中成本最小的節點
        :return: 最小成本的位置
        """
        def calc(a, b):
            return a + b * 2

        pos_x, pos_y = self.open_set[0]
        min_f = calc(self.cost_set[pos_y][pos_x], self.get_h((pos_x, pos_y)))
        index = 0
        for i, (x, y) in enumerate(self.open_set):
            temp_val = calc(self.cost_set[y][x], self.get_h((x, y)))
            if temp_val < min_f:
                pos_x = x
                pos_y = y
                min_f = temp_val
                index = i
        self.open_set.pop(index)
        self.close_set[pos_y][pos_x] = 1
        return pos_x, pos_y

    def check_move(self, location):
        if self.map[location[1], location[0]] == 1:
            return False
        return True

    def append(self, location):
        check_list = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]

        for step_x, step_y in check_list:
            pos_x = location[0] + step_x
            pos_y = location[1] + step_y

            if self.close_set[pos_y][pos_x] == 1:
                continue

            if not self.check_move((pos_x, pos_y)):
                continue

            step_cost = (step_x ** 2 + step_y ** 2) ** 0.5
            old_cost = self.cost_set[location[1]][location[0]]
            new_cost =  old_cost + step_cost

            if (new_cost < old_cost) or ((pos_x, pos_y) not in self.open_set):
                self.come[pos_y][pos_x] = location
                self.cost_set[pos_y][pos_x] = new_cost
                self.open_set.append((pos_x, pos_y))

    def get_path(self, location):
        path = [location]
        x, y = location
        while (x, y) != self.start:
            up_x, up_y = self.come[y][x]
            path.append((up_x, up_y))
            x = up_x
            y = up_y
        path.reverse()
        self.path = path

        img = cv2.imread(os.path.join(os.getcwd(), 'maps_img', self.file[:-4] + '.png'))
        for x,y in path:
            for i,j in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                img[y + (j * SIZE), x + (i * SIZE)] = np.array([100 * (i + 1), 0, 100 * (j + 1)])
        cv2.imwrite(os.path.join(os.getcwd(), 'res', self.file[:-4] + '.png'), img)

        return path

    def search(self):
        roll = rolling()

        # 將初始位置放入估計列表中
        self.open_set.append(self.start)
        while self.open_set:
            next(roll)
            # 在open set中取出最小成本的位置
            pos_x, pos_y = self.get_min()
            # 查看是否為終點
            if (pos_x == self.end[0]) and (pos_y == self.end[1]):
                # 重建路逕
                self.get_path((pos_x, pos_y))
                return True
            self.append((pos_x, pos_y))
        return False
