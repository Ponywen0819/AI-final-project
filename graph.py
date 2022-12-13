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

    def div(self, val):
        for d in val:
            # 檢查是否有需要切割的區域
            i = 0
            while i < len(self.region_white):
                region_white = self.region_white
                region_now = region_white[i]
                y = region_now[1]
                h = region_now[3]
                diff = d - y
                if (diff < h) and (diff > 0):
                    region1 = [region_now[0], region_now[1], region_now[2], diff]
                    region2 = [region_now[0], region_now[1] + diff, region_now[2], h - diff]
                    self.region_white = region_white[0:i] + [region1, region2] + region_white[i+1:]
                    i += 2
                else:
                    i += 1

    def get_pixel(self, x, y):
        pix = self.map[y, x]
        if (pix == 2) or (pix == 3):
            pix = 0
        return pix

    def gen_graph(self):
        # 用於儲存圖
        g = [Vertex(v) for v in self.region_white]
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
    def get_h(x_1, y_1, x_2, y_2):
        return ((x_1 - x_2) ** 2 + (y_1 - y_2) ** 2) ** 0.5

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
            old = self.get_h(min_region.x, min_region.y, end_reg.x, end_reg.y)
            for tentative in open_set:
                new = self.get_h(tentative.x, tentative.y, end_reg.x, end_reg.y)
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
                    path.append(self.graph[p_i])
                    p_i = path_set[p_i]
                return path
            for con in min_region.connect:
                if check[self.graph.index(con)] == 1:
                    continue
                if con not in open_set:
                    path_set[self.graph.index(con)] = min_index
                    open_set.append(con)
        return None

    def cutting(self):
        print('Start Cutting')
        for x in range(self.map.shape[1]):
            # 尋找新線段
            pix = self.map[0, x]
            temp = [0]
            for y in range(1, self.map.shape[0]):
                now = self.get_pixel(x, y)
                if now != pix:
                    temp.extend([y, pix, y])
                pix = self.get_pixel(x, y)
            temp.extend([self.map.shape[0], pix])

            # 將新線條加入舊圖形中
            # (x, y, w, h)
            while temp:
                # 將線段取出
                y_1, y_2, t = temp[:3]
                temp = temp[3:]

                # 檢查是否有符合的舊圖形
                been_fit = False
                region_list = self.region_white if (t == 0) else self.region_black
                for i, r in enumerate(region_list):
                    if (r[0] + r[2] == x) and (r[1] == y_1) and (r[3] == y_2 - y_1):
                        r[2] += 1
                        been_fit = True
                # 若無符合的圖形則創建圖形
                if not been_fit:
                    region_list.append([x, y_1, 1, y_2 - y_1])
        # 將水平分割座標取出
        div_y = []
        for i in self.region_black:
            if i[1] not in div_y:
                div_y.append(i[1])

            if (i[1] + i[3]) not in div_y:
                div_y.append(i[1] + i[3])

        # 切割區域
        self.div(div_y)

        # 建立圖
        self.gen_graph()




# map = np.genfromtxt(os.path.join(os.getcwd(), 'maps_csv', 'test.csv'), delimiter=',')
# a = CellDec(map)
#
# a.cutting()
# a.search((20, 5), (90, 92))