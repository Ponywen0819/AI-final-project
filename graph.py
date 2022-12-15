import math

import cv2
import numpy as np
import os
from rolling import rolling

class Vertex:
    def __init__(self, info):
        self.x = info[0]
        self.y = info[1]
        self.w = info[2]
        self.h = info[3]
        self.connect = []

    def __str__(self):
        return "x: %d, y: %d, w: %d, h: %d" %(self.x, self.y, self.w, self.h)

class CellDec:
    def __init__(self, map_data: np.ndarray):
        self.map = map_data
        # 用來紀錄線段
        self.region_black = []
        self.region_white = []
        # 用來記錄圖
        self.graph = []
        # 用來存放可能是圓形的圖形
        self.maybe = []

    def get_pixel(self, x, y):
        pix = self.map[y, x]
        if (pix == 2) or (pix == 3):
            pix = 0
        return pix

    def gen_graph(self, regions):
        # 用於儲存圖
        g = [Vertex(v) for v in regions]
        # 遍歷所有區域
        for target in g:
            for i in g:
                if i == target:
                    continue
                # 判斷在x軸上使否相鄰
                x_lower_bound = target.x - i.w
                x_higher_bound = target.x + target.w
                near_x = (i.x >= x_lower_bound) and (i.x <= x_higher_bound)
                # 判斷在y軸上是否相鄰
                y_lower_bound = target.y - i.h
                y_higher_bound = target.y + target.h
                near_y = (i.y >= y_lower_bound) and (i.y <= y_higher_bound)

                count = 0
                count = count + 1 if (i.x == x_lower_bound) else count
                count = count + 1 if (i.x == x_higher_bound) else count
                count = count + 1 if (i.y == y_lower_bound) else count
                count = count + 1 if (i.y == y_higher_bound) else count

                if count >= 2:
                    continue

                # 新增路逕
                if near_y and near_x:
                    target.connect.append(i)
        self.graph = g

    def get_spec_region(self, location):
        for i in self.graph:
            x_lower_bound = i.x
            x_higher_bound = i.x + i.w
            x_check = (location[0] >= x_lower_bound) and (location[0] < x_higher_bound)

            y_lower_bound = i.y
            y_higher_bound = i.y + i.h
            y_check = (location[1] >= y_lower_bound) and (location[1] < y_higher_bound)

            if x_check and y_check:
                return i

    @staticmethod
    def get_dis(x_1, y_1, x_2, y_2):
        return ((x_1 - x_2) ** 2 + (y_1 - y_2) ** 2) ** 0.5

    def draw(self, f, regions, t: ''):
        img = cv2.imread(os.path.join(os.getcwd(), 'maps_img', f[:-4] + '.png'))
        for i in regions:
            for x in range(i[2]):
                img[i[1], i[0] + x] = np.array([50, 255, 0])
                # img[i[1] + i[3] - 1, i[0] + x] = np.array([255, 100, 0])
            for y in range(i[3]):
                img[i[1] + y, i[0]] = np.array([100, 50, 255])
                # img[i[1] + y, i[0] + i[2] - 1] = np.array([200, 100, 34])
        cv2.imwrite(os.path.join(os.getcwd(), 'res', f[:-4] + t +'.png'), img)

    def search(self, start, end):
        print("Starting Searching")
        roll = rolling()
        start_reg = self.get_spec_region(start)
        end_reg = self.get_spec_region(end)

        # 用於存放以查找的區域
        check = [0 for i in range(len(self.graph))]

        # 將初始位置放入估計列表中
        open_set = [start_reg]
        path_set = [-1 for i in range(len(self.graph))]
        while open_set:
            next(roll)
            # 在open set中取出最小成本的位置
            min_region = open_set[0]
            old_h = self.get_dis(min_region.x, min_region.y, end_reg.x, end_reg.y)
            old_c = self.get_dis(min_region.x, min_region.y, start_reg.x, start_reg.y)
            old = old_c + old_h
            for tentative in open_set:
                new_h = self.get_dis(tentative.x, tentative.y, end_reg.x, end_reg.y)
                new_c = self.get_dis(tentative.x, tentative.y, start_reg.x, start_reg.y)
                new = new_c + new_h
                if new < old:
                    old = new
                    min_region = tentative

            open_set.remove(min_region)
            min_index = self.graph.index(min_region)
            check[min_index] = 1
            # 查看是否為終點
            if min_region == end_reg:
                # 重建路逕
                # self.get_path(min_region)
                path = []
                p_i = min_index
                while p_i != -1:
                    n = self.graph[p_i]
                    path.append([n.x, n.y, n.w, n.h])
                    p_i = path_set[p_i]
                return path
            for con in min_region.connect:
                if check[self.graph.index(con)] == 1:
                    continue
                if con not in open_set:
                    path_set[self.graph.index(con)] = min_index
                    open_set.append(con)
        return None

    def getLines(self):
        print('Start finding lines')
        # 用來存放還在計算的線段
        open_line = []
        # 用來存放計算完的線段
        close_line = []
        for x in range(self.map.shape[1]):
            # 尋找邊緣
            pix = self.map[0, x]
            temp = []
            # temp = [] if pix == 0 else [0]
            for y in range(1, self.map.shape[0]):
                now = self.get_pixel(x, y)
                if now != pix:
                    # temp.append(y if now == 1 else y - 1)
                    temp.append(y)
                pix = self.get_pixel(x, y)
            i = 0
            # 檢查線段是否封閉
            while i < len(open_line):
                if open_line[i][2] != (x - 1):
                    # 如果是點 或是太短 則跳過
                    if abs(open_line[i][0] - open_line[i][2]) > (self.map.shape[1] // 100):
                        open_line[i][2] += 1
                        close_line.append(open_line[i])
                    open_line.pop(i)
                else:
                    i += 1
            # 每條線為(x_1, y_1, x_2, y_2)
            # 選擇對於線段最近的邊緣
            for edge in temp:
                found = False
                for line in open_line:
                    # line = open_line[i]
                    new_diff = abs(edge - line[3])
                    old_diff = abs(line[1] - line[3])
                    # 如果是點 且 新點的角度小於45
                    if (line[0] == line[2]) and (line[1] == line[3]) and  (new_diff <= 1):
                        found = True
                    # 如果是水平線 且 新角度也必須是0
                    elif (old_diff == 0) and (new_diff == 0):
                        found = True
                    # 如果是曲線 且 新角度必須小於45
                    elif new_diff <= 1:
                        found = True
                    if found:
                        line[2] += 1
                        line[3] = edge
                        break
                # 如果是新的點
                if not found:
                    open_line.append([x, edge, x, edge])

        for i in open_line:
            i[2] += 1
            close_line.append(i)

        return close_line

    def check_region_type(self, r):
        x, y, w, h = r
        x_2 = x + w
        y_2 = y + h
        white = 0
        black = 0
        step_x = w/10
        step_y = h/10

        # print(r)
        while (x < x_2) and (y < y_2):

            if self.map[int(y), int(x)] == 0:
                white += 1
            else:
                black += 1
            x += step_x
            y += step_y
        return white > black
    def get_regions(self, lines):
        print("Starting Cutting")
        # 將地圖上的斷點取出
        location_x = []
        location_y = []
        for line in lines:
            for i in range(0, 4, 2):
                if line[i] not in location_x:
                    location_x.append(line[i])
                if line[i + 1] not in location_x:
                    location_y.append(line[i + 1])
        location_x.sort()
        location_y.sort()
        regions = [[0, 0, self.map.shape[1], self.map.shape[0]]]
        # 使用斷點將地圖分割
        for y in location_y:
            i = 0
            while i < len(regions):
                region_now = regions[i]
                h = region_now[3]
                diff = y - region_now[1]
                if diff < (self.map.shape[0] // 100):
                    i+=1
                    continue
                if (diff < h) and (diff > 0):
                    region1 = [region_now[0], region_now[1], region_now[2], diff]
                    region2 = [region_now[0], region_now[1] + diff, region_now[2], h - diff]
                    regions = regions[0:i] + [region1, region2] + regions[i + 1:]
                    i += 2
                else:
                    i += 1
        for x in location_x:
            i = 0
            while i < len(regions):
                region_now = regions[i]
                w = region_now[2]
                diff = x - region_now[0]
                if diff < (self.map.shape[1] // 100):
                    i+=1
                    continue
                if (diff < w) and (diff > 0):
                    region1 = [region_now[0], region_now[1], diff, region_now[3]]
                    region2 = [region_now[0] + diff, region_now[1],  w - diff, region_now[3]]
                    regions = regions[0:i] + [region1, region2] + regions[i + 1:]
                    i += 2
                else:
                    i += 1
        regions = [reg for reg in regions if self.check_region_type(reg)]
        return regions

    def draw_line(self, f, lines, w: 1):
        img = cv2.imread(os.path.join(os.getcwd(), 'maps_img', f[:-4] + '.png'))
        for line in lines:
            img = cv2.circle(img, (line[0], line[1]), radius=w - 1, color=(0, 0, 255), thickness=-1)
            img = cv2.circle(img, (line[2], line[3]), radius=w - 1, color=(255, 0, 0), thickness=-1)
            # cv2.line(img, line[:2], line[2:4], (255, 0, 0), w)
        cv2.imwrite(os.path.join(os.getcwd(), 'res', f[:-4] + '_lines.png'), img)


# map = np.genfromtxt(os.path.join(os.getcwd(), 'maps_csv', 'test.csv'), delimiter=',')
# a = CellDec(map)
#
# a.cutting()
# a.search((20, 5), (90, 92))