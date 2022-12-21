import cv2
import numpy as np
import math
from rolling import rolling
import collections

SIZE = 10


class CCPP:
    def __init__(self, start: tuple, map: np.ndarray):
        self.map = map
        self.w = map.shape[1]
        self.h = map.shape[0]
        self.start = start
        # 用於存放各節點是否造訪過
        self.visited = np.zeros(map.shape[:2], dtype=bool)
        # 用於表示不重複的點
        self.overlapping = np.zeros(map.shape[:2], dtype=bool)

        self.path = []

        # D*帶展開的節點
        self.open_list = collections.deque()
        # 用於存放全地圖的cost
        self.cost = np.full(map.shape[:2], -1).astype(float)
        # 節點的父節點
        self.b_x = np.zeros((self.h, self.w), dtype=int)
        self.b_y = np.zeros((self.h, self.w), dtype=int)
        # 初始化資料
        self.enlarge_map()  # 放大障礙物邊框
        self.get_cost_map()

    @staticmethod
    def get_distance(x_1, y_1, x_2, y_2):
        return ((x_1 - x_2) ** 2 + (y_1 - y_2) ** 2) ** 0.5

    def enlarge_map(self):
        print('Start enlarge map')
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
                for i in range(x - SIZE, x + SIZE):
                    for j in range(y - SIZE, y + SIZE):
                        if self.get_distance(x, y, i, j) < SIZE:
                            try:
                                res[j, i] = 1
                            except:
                                pass
        # 地圖邊緣膨脹
        for y in range(-1, self.map.shape[0] + 1):
            for i in range(-SIZE, SIZE):
                for j in range(-SIZE, SIZE):
                    if self.get_distance(-1, y, i - 1, j + y) < SIZE:
                        try:
                            res[j + y, i - 1] = 1
                        except:
                            pass
        for x in range(-1, self.map.shape[1] + 1):
            for i in range(-SIZE, SIZE):
                for j in range(-SIZE, SIZE):
                    if self.get_distance(x, -1, i + x, j - 1) < SIZE + 0.5:
                        try:
                            res[j - 1, i + x] = 1
                        except:
                            pass

        img = cv2.imread('maps_img/small-hard.png')
        for x in range(img.shape[1]):
            for y in range(img.shape[0]):
                img[y, x] = np.array([255, 255, 255] if res[y, x] == 0 else [0, 0, 0])
        cv2.imwrite('res/small-hard-large.png', img)
        self.map = res

    # 將全地圖節點織成本算出
    def get_cost_map(self):
        print('Start calc cost')

        self.open_list.append(self.start)
        self.cost[self.start[1], self.start[0]] = 0
        self.b_x[self.start[1], self.start[0]] = self.start[0]
        self.b_y[self.start[1], self.start[0]] = self.start[1]
        while self.open_list:
            # 選擇待展開節點優先度最大的
            append = self.open_list.popleft()
            print(append, end='\r')

            father_cost = self.cost[append[1], append[0]]

            # 直線個展開方向
            for step_x, step_y in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                next_x = append[0] + step_x
                next_y = append[1] + step_y
                next_cost = father_cost + 1
                try:
                    # 如果是障礙物則跳過
                    if self.map[next_y, next_x] == 1:
                        continue
                    # 如果節點已被展開 判斷是此節點是否為較好的路徑
                    if (self.cost[next_y, next_x] < next_cost) and (self.cost[next_y, next_x] != -1):
                        continue

                    elif self.cost[next_y, next_x] != -1:
                        self.cost[next_y, next_x] = next_cost
                        self.b_x[next_y, next_x] = append[0]
                        self.b_y[next_y, next_x] = append[1]
                    else:
                        self.cost[next_y, next_x] = next_cost
                        self.b_x[next_y, next_x] = append[0]
                        self.b_y[next_y, next_x] = append[1]
                        self.open_list.append((next_x, next_y))
                except IndexError:
                    pass
            # 斜角展開方向
            for step_x, step_y in [(1, 1), (-1, 1), (-1, -1), (1, -1)]:
                next_x = append[0] + step_x
                next_y = append[1] + step_y
                next_cost = father_cost + 1.4
                try:
                    # 如果是障礙物則跳過
                    if self.map[next_y, next_x] == 1:
                        continue
                    # 如果節點已被展開 判斷是此節點是否為較好的路徑
                    if (self.cost[next_y, next_x] < next_cost) and (self.cost[next_y, next_x] != -1):
                        continue
                    elif self.cost[next_y, next_x] != -1:
                        self.cost[next_y, next_x] = next_cost
                        self.b_x[next_y, next_x] = append[0]
                        self.b_y[next_y, next_x] = append[1]
                    else:
                        self.cost[next_y, next_x] = next_cost
                        self.b_x[next_y, next_x] = append[0]
                        self.b_y[next_y, next_x] = append[1]
                        self.open_list.append((next_x, next_y))
                except IndexError:
                    pass

        print()

    def set_visited(self, pos):
        for x in range(pos[0] - SIZE // 2, pos[0] + SIZE // 2 + 1):
            for y in range(pos[1] - SIZE // 2, pos[1] + SIZE // 2 + 1):
                try:
                    self.visited[y, x] = True
                except:
                    pass

    def set_overlap(self, pos):
        for x in range(pos[0] - SIZE, pos[0] + SIZE + 1):
            for y in range(pos[1] - SIZE, pos[1] + SIZE + 1):
                try:
                    self.overlapping[y, x] = True
                except:
                    pass

    def search(self, start):
        # 找到離自己最近的
        # 1. 未探索的點
        # 2. 在貼近障礙物，且裡面有未探詢的點

        cost = np.full((self.h, self.w), -1).astype(float)
        # 節點的父節點
        b_x = np.zeros((self.h, self.w), dtype=int)
        b_y = np.zeros((self.h, self.w), dtype=int)

        open_list = collections.deque([start])
        cost[self.start[1], self.start[0]] = 0
        b_x[self.start[1], self.start[0]] = self.start[0]
        b_y[self.start[1], self.start[0]] = self.start[1]

        ans = None

        while open_list:
            append = open_list.popleft()
            # print(append, end='\r')

            # 判斷是否為未判訪過之節點
            if self.visited[append[1], append[0]] == False:
                ans = append
                break
            # 是否在貼近障礙物
            by_obstacle = False
            for step_x, step_y in [(1,0), (-1,0), (0, 1), (0, -1)]:
                check_x = append[0] + step_x
                check_y = append[1] + step_y
                if self.map[check_y, check_x] == 1:
                    by_obstacle = True
                    break
            exist = False
            # 是否在範圍內有位尋訪節點
            for x in range(append[0] - SIZE // 2, append[0] + SIZE // 2 + 1):
                for y in range(append[1] - SIZE // 2, append[1] + SIZE // 2 + 1):
                    if self.visited[y, x] == False:
                        exist = True
                        break
                if exist:
                    break

            if exist and by_obstacle:
                ans = append
                break


            father_cost = cost[append[1], append[0]]

            # 直線個展開方向
            for step_x, step_y in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                next_x = append[0] + step_x
                next_y = append[1] + step_y
                next_cost = father_cost + 1
                try:
                    # 如果是障礙物則跳過
                    if self.map[next_y, next_x] == 1:
                        continue
                    # 如果節點已被展開 判斷是此節點是否為較好的路徑
                    if (cost[next_y, next_x] < next_cost) and (cost[next_y, next_x] != -1):
                        continue

                    elif cost[next_y, next_x] != -1:
                        cost[next_y, next_x] = next_cost
                        b_x[next_y, next_x] = append[0]
                        b_y[next_y, next_x] = append[1]
                    else:
                        cost[next_y, next_x] = next_cost
                        b_x[next_y, next_x] = append[0]
                        b_y[next_y, next_x] = append[1]
                        open_list.append((next_x, next_y))
                except IndexError:
                    pass
            # 斜角展開方向
            for step_x, step_y in [(1, 1), (-1, 1), (-1, -1), (1, -1)]:
                next_x = append[0] + step_x
                next_y = append[1] + step_y
                next_cost = father_cost + 1.4
                try:
                    # 如果是障礙物則跳過
                    if self.map[next_y, next_x] == 1:
                        continue
                    # 如果節點已被展開 判斷是此節點是否為較好的路徑
                    if (cost[next_y, next_x] < next_cost) and (cost[next_y, next_x] != -1):
                        continue
                    elif cost[next_y, next_x] != -1:
                        cost[next_y, next_x] = next_cost
                        b_x[next_y, next_x] = append[0]
                        b_y[next_y, next_x] = append[1]
                    else:
                        cost[next_y, next_x] = next_cost
                        b_x[next_y, next_x] = append[0]
                        b_y[next_y, next_x] = append[1]
                        open_list.append((next_x, next_y))
                except IndexError:
                    pass

            print()

        if ans == None:
            return None
        else:
            path = [ans]
            while path[0] != start:
                now = path[0]
                path.insert(0, (b_x[now[1], now[0]], b_y[now[1], now[0]]))

            return path

    # 計算路徑
    def coverage(self):
        radius = SIZE // 2
        # 這裡會以邊長為SIZE + 1的正方形去做運算
        current = self.start
        c_x = current[0]
        c_y = current[1]
        path = [current]

        append = collections.deque([current])
        last = 0
        while append:
            # 將現在的位置標記上已造訪
            # print(path[-1], end='')

            self.set_visited(current)

            self.set_overlap(current)


            next_move = None
            for check_x, check_y in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                next_x = c_x + check_x * SIZE + check_x
                next_y = c_y + check_y * SIZE + check_y
                try:
                    if (self.overlapping[next_y, next_x] == False) and (self.cost[next_y, next_x] != -1):
                        if next_move is None:
                            next_move = (next_x, next_y)
                        elif self.cost[next_y, next_x] < self.cost[next_move[1], next_move[0]]:
                            next_move = (next_x, next_y)
                except:
                    pass
            if next_move is None:
                next_move = self.search(current)
                if next_move != None:
                    for p in next_move:
                        self.set_visited(p)
                        self.set_overlap(p)
                    current = next_move[-1]
                    c_x = current[0]
                    c_y = current[1]
                    path.extend(next_move)
                else:
                    break
            else:
                current = next_move
                c_x = current[0]
                c_y = current[1]
                path.append(next_move)

        self.path = path

        # img = cv2.imread('res/small-hard-large.png')
        # for i in range(1, len(self.path)):
        #     cv2.line(img, self.path[i - 1], self.path[i], (200, 100, 100), 1)
        # cv2.imwrite('res/test-line.png', img)


    def back_home(self):
        current = self.path[-1]
        c_x = current[0]
        c_y = current[1]
        path = [current]

        while 1:
            print((c_x, c_y), end='\r')
            next_x = self.b_x[c_y, c_x]
            next_y = self.b_y[c_y, c_x]
            c_x = next_x
            c_y = next_y

            path.append((next_x, next_y))
            if (next_x, next_y) == self.start:
                break

        self.path.extend(path)


        img = cv2.imread('maps_img/small-hard.png')
        for i in range(1, len(self.path)):
            cv2.circle(img, self.path[i], SIZE, (200, 100, 100), -1)
            # cv2.line(img, self.path[i - 1], self.path[i], (200, 100, 100), 1)
        cv2.imwrite('res/test-line.png', img)
        # print(path)
