import collections
from rolling import rolling
import numpy as np
import cv2
import map_process

SIZE = 10

class SPP:
    def __init__(self, start, end, map, file):
        self.start = start
        self.end = end
        self.map = map_process.map_enlarge(map)
        self.file = file
        self.step = 0
        self.spin = 0

    def search(self):
        end = self.end
        start = self.start
        map = self.map
        cost = np.full(map.shape, -1).astype(float)
        # 節點的父節點
        b_x = np.zeros(map.shape, dtype=int)
        b_y = np.zeros(map.shape, dtype=int)

        open_list = collections.deque([end])
        cost[end[1], end[0]] = 0
        b_x[end[1], end[0]] = end[0]
        b_y[end[1], end[0]] = end[1]

        ans = None

        while open_list:
            append = open_list.popleft()
            # print(append, end='\r')

            if append == start:
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
                    if map[next_y, next_x] == 1:
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
                    if map[next_y, next_x] == 1:
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

        if ans is None:
            return None
        else:
            path = [ans]
            dir_x = ans[0] - b_x[ans[1], ans[0]]
            dir_y = ans[1] - b_y[ans[1], ans[0]]
            while path[0] != end:
                now = path[0]
                next_step = (b_x[now[1], now[0]], b_y[now[1], now[0]])

                next_dir_x = now[0] - next_step[0]
                next_dir_y = now[1] - next_step[1]

                if(next_dir_x == dir_x) and (next_dir_y == dir_y):
                    self.step += 1
                elif(next_dir_x == dir_x) and (next_dir_y == dir_y):
                    self.step += 1
                else:
                    self.spin += 1
                    self.step += 1
                    dir_x = next_dir_x
                    dir_y = next_dir_y

                path.insert(0, next_step)


            img = cv2.imread('maps_img/' + self.file + '.png')
            for i in range(0, len(path)):
                cv2.circle(img, path[i], 10, (163, 200, 150), -1)
            cv2.imwrite('res/' + self.file + '_shortest.png', img)



            return path