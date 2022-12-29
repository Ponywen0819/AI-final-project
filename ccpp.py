import cv2
import numpy as np
from rolling import rolling
import collections
import map_process

SIZE = 6


class CCPP:
    def __init__(self, start: tuple, map: np.ndarray, file):
        self.file = file

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
        self.map = map_process.map_enlarge(map)
        self.get_cost_map()

        self.can_reach = 0
        self.reached = np.zeros((self.h,self.w))

        # 紀錄總步數
        self.step = 0
        # 記錄旋轉次數
        self.spin = 0

    # 將全地圖節點織成本算出
    def get_cost_map(self):
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
        print('done')
    def set_visited(self, pos):
        # for x in range(pos[0] - SIZE, pos[0] + SIZE + 1):
        #     for y in range(pos[1] - SIZE, pos[1] + SIZE + 1):
        #         try:
        #             self.visited[y, x] = True
        #         except:
        #             pass
        x_down = pos[0] - SIZE
        x_up = pos[0] + SIZE + 1
        y_down = pos[1] - SIZE
        y_up = pos[1] + SIZE + 1

        if x_down < 0:
            x_down = 0
        if x_up > self.w:
            x_up = self.w
        if y_down < 0:
            y_down = 0
        if y_up > self.h:
            y_up = self.h
        self.visited[y_down: y_up, x_down:x_up] = True
    def set_overlap(self, pos):
        # for x in range(pos[0] - (SIZE * 2), pos[0] + (SIZE * 2) + 1):
        #     for y in range(pos[1] - (SIZE * 2), pos[1] + (SIZE * 2) + 1):
        #         try:
        #             self.overlapping[y, x] = True
        #         except:
        #             pass
        x_down = pos[0] - (SIZE * 2)
        x_up = pos[0] + (SIZE * 2) + 1
        y_down = pos[1] - (SIZE * 2)
        y_up = pos[1] + (SIZE * 2) + 1

        if x_down < 0:
            x_down = 0
        if x_up > self.w:
            x_up = self.w
        if y_down < 0:
            y_down = 0
        if y_up > self.h:
            y_up = self.h
        self.overlapping[y_down: y_up, x_down:x_up] = True

    def set_reached(self, pos):
        y, x = np.ogrid[0:self.h, 0:self.w]

        mask = (x - pos[0]) ** 2 + (y - pos[1]) ** 2 <= 100

        self.reached[mask] = True
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
            x_down = append[0] - 6
            x_up = append[0] + 7
            y_down = append[1] - 6
            y_up = append[1] + 7

            if x_down < 0:
                x_down = 0
            if x_up > self.w:
                x_up = self.w
            if y_down < 0:
                y_down = 0
            if y_up > self.h:
                y_up = self.h

            if (self.visited[y_down: y_up, x_down:x_up] == False).any():
                exist = True

            if exist and by_obstacle:
                ans = append
                break


            father_cost = cost[append[1], append[0]]

            # 直線個展開方向
            for step_x, step_y in [(1, 0), (0, 1), (-1, 0), (0, -1),(1, 1), (-1, 1), (-1, -1), (1, -1)]:
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

        if ans == None:
            return None
        else:
            path = [ans]
            self.set_visited(ans)
            self.set_overlap(ans)
            self.set_reached(ans)
            while path[0] != start:
                now = path[0]
                self.set_visited(now)
                self.set_overlap(now)
                self.set_reached(now)
                path.insert(0, (b_x[now[1], now[0]], b_y[now[1], now[0]]))

            return path

    # 計算路徑
    def coverage(self):
        # 這裡會以邊長為SIZE + 1的正方形去做運算
        current = self.start
        c_x = current[0]
        c_y = current[1]
        path = [current]

        append = collections.deque([current])
        last = 0
        # 設定初始機器人方向
        direction = (1, 0)
        while append:
            # 將現在的位置標記上已造訪
            self.set_visited(current)
            self.set_overlap(current)
            self.set_reached(current)

            next_move = None
            for check_x, check_y in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                next_x = c_x + check_x * (SIZE * 2) + check_x
                next_y = c_y + check_y * (SIZE * 2) + check_y
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
                        dir_x = p[0] - current[0]
                        dir_y = p[1] - current[1]
                        if (dir_x, dir_y) == direction:
                            self.step += 1
                        elif (-dir_x, -dir_y) == direction:
                            self.step += 1
                        else:
                            self.step += 1
                            self.spin += 1
                            direction = (dir_x, dir_y)

                        current = p
                    c_x = current[0]
                    c_y = current[1]
                    path.extend(next_move)
                else:
                    break
            else:
                dir_x = next_move[0] - current[0]
                dir_y = next_move[1] - current[1]
                if (dir_x, dir_y) == direction:
                    self.step += 11
                elif (-dir_x, -dir_y) == direction:
                    self.step += 11
                else:
                    self.step += 11
                    self.spin += 1
                    direction = (dir_x, dir_y)
                current = next_move
                c_x = current[0]
                c_y = current[1]
                path.append(next_move)

        self.path = path

    def back_home(self):
        current = self.path[-1]
        c_x = current[0]
        c_y = current[1]
        path = [current]

        while 1:
            next_x = self.b_x[c_y, c_x]
            next_y = self.b_y[c_y, c_x]
            c_x = next_x
            c_y = next_y

            path.append((next_x, next_y))
            if (next_x, next_y) == self.start:
                break

        self.path.extend(path)

        rrrr = [(163, 200, 150), (13, 200, 10)]
        img = cv2.imread('maps_img/' + self.file + '.png')
        for i in range(0, len(self.path)):
            cv2.line(img, self.path[i - 1], self.path[i], rrrr[i%2], 20)
            # cv2.circle(img, self.path[i], 10 , rrrr[i % 2], -1)
        cv2.imwrite('res/' + self.file + '_coverage.png', img)

        img2 = cv2.imread('maps_img/' + self.file + '.png')
        for i in range(1, len(self.path)):
            cv2.line(img2, self.path[i - 1], self.path[i], rrrr[i%2], 1)
        cv2.imwrite('res/' + self.file + '_ccpp_path.png', img2)

    def get_can_reached(self):
        def enlarge_circle(c_x, c_y, map):
            y, x = np.ogrid[0:map.shape[0], 0:map.shape[0]]

            mask = (x - c_x) ** 2 + (y - c_y) ** 2 <= 100

            map[mask] = 0

        res = np.copy(self.map)

        for y in range(self.h):
            for x in range(self.w):
                if self.map[y, x] == 1:
                    continue
                if (self.map[y, x] == 2) or (self.map[y, x] == 3):
                    res[y, x] = 0
                    continue
                # 檢查是否是障礙物邊緣
                is_edge = False
                for i, j in [(0, 1), (1, 0), (-1, 0), (0, -1)]:
                    next_x = x + i
                    next_y = y + j
                    if (next_y < 0) or (next_y > (self.map.shape[0] - 1)):
                        continue
                    if (next_x < 0) or (next_x > (self.map.shape[1] - 1)):
                        continue
                    if int(self.map[next_y, next_x]) == 1:
                        is_edge = True
                if not is_edge:
                    continue
                enlarge_circle(x, y, res)
        self.can_reach = np.count_nonzero(res == 0)





