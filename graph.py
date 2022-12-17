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
        self.rr = rolling()
    def __str__(self):
        return "x: %d, y: %d, w: %d, h: %d" %(self.x, self.y, self.w, self.h)

class CellDec:
    def __init__(self, map_data: np.ndarray):
        self.map = map_data
        self.path = []
        self.regions = []
        self.graph = []
        self.lines = []

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

    def draw(self, f, regions, t:str = ''):
        img = cv2.imread(os.path.join(os.getcwd(), 'maps_img', f[:-4] + '.png'))
        for i in regions:
            for x in range(i[2]):
                img[i[1], i[0] + x] = np.array([50, 255, 0])
                img[i[1] + i[3] - 1, i[0] + x] = np.array([255, 100, 0])
            for y in range(i[3]):
                img[i[1] + y, i[0]] = np.array([100, 50, 255])
                img[i[1] + y, i[0] + i[2] - 1] = np.array([200, 100, 34])
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
            old = old_c * 3 + old_h
            for tentative in open_set:
                new_h = self.get_dis(tentative.x, tentative.y, end_reg.x, end_reg.y)
                new_c = self.get_dis(tentative.x, tentative.y, start_reg.x, start_reg.y)
                new = new_c * 3 + new_h
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
                    self.path = path
                return path
            for con in min_region.connect:
                if check[self.graph.index(con)] == 1:
                    continue
                if con not in open_set:
                    path_set[self.graph.index(con)] = min_index
                    open_set.append(con)
        return None

    def big(self):

        print(self.map.shape)
        SIZE = 10
        # 做x軸膨脹
        for x in range(self.map.shape[1]):
            pix = self.map[0, x]
            temp = []
            for y in range(1, self.map.shape[0]):
                now = self.get_pixel(x, y)
                if now != pix:
                    temp.append((y, now))
                pix = self.get_pixel(x, y)
            # 開始膨脹
            for t in temp:
                # 判斷顏色 如果是白的就往下長
                offest = 0
                step = 1
                if t[1] != 0:
                    offest = 1
                    step = -1
                y_now = t[0]
                i = 0
                while i < (SIZE + offest):
                    if y_now >= self.map.shape[0]:
                        break
                    self.map[y_now, x] = 1
                    y_now += step
                    i += 1
        # 做y軸膨脹
        for y in range(self.map.shape[0]):
            pix = self.map[y, 0]
            temp = []
            for x in range(1, self.map.shape[1]):
                now = self.get_pixel(x, y)
                if now != pix:
                    temp.append((x, now))
                pix = self.get_pixel(x, y)
            # 開始膨脹
            for t in temp:
                # 判斷顏色 如果是白的就往下長
                offest = 0
                step = 1
                if t[1] != 0:
                    offest = 1
                    step = -1
                x_now = t[0]
                i = 0
                while i < (SIZE + offest):
                    if x_now >= self.map.shape[1]:
                        break
                    self.map[y, x_now] = 1
                    x_now += step
                    i += 1
        return self.map

    def getLines(self):
        self.big()
        print('Start finding lines')
        # 用來存放還在計算的線段
        open_line = []
        # 用來存放計算完的線段
        close_line = []
        for x in range(self.map.shape[1]):
            # 尋找邊緣
            pix = self.map[0, x]
            temp = [0] if pix == 0 else []
            for y in range(1, self.map.shape[0]):
                now = self.get_pixel(x, y)
                if now != pix:
                    if now == 0:
                        temp.append(y)
                    else:
                        temp.append(y - 1)
                    # temp.append(y)
                pix = self.get_pixel(x, y)
            i = 0
            if pix == 0:
                temp.append(self.map.shape[0] - 1)
            # 檢查線段是否封閉
            while i < len(open_line):
                if open_line[i][2] != (x - 1):
                    # 如果是點 或是太短 則跳過
                    if abs(open_line[i][0] - open_line[i][2]) > (self.map.shape[1] // 100):
                        # open_line[i][2] += 1
                        close_line.append(open_line[i])
                    open_line.pop(i)
                else:
                    i += 1
            # 每條線為(x_1, y_1, x_2, y_2)
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
            close_line.append(i)
        print(len(close_line))

        return close_line

    def check_region_type(self, r) :
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


    def find_closest_line(self, lines, target) -> int:
        # 確認線條是往上還往下
        line_x = target[0]

        line_y = target[1] - 1
        if line_y < 0:
            step = 1
        else:
            step = -1 if self.map[line_y, line_x] == 0 else 1

        # 用來存放結果
        res = -1
        # 將檢查集合內的線段
        for l_i, other_line in enumerate(lines):
            if (step == 1) and (other_line[1] < target[1]):
                continue
            elif (step == -1) and (other_line[1] > target[1]):
                continue
            # 判斷是否在區域內
            judge = 0
            for i in range(2):
                for j in range(2):
                    if (target[i * 2] - other_line[j * 2]) < 0:
                        judge += 1
            # 不再區域內則跳過
            if (judge == 0) or (judge == 4):
                continue

            if res == -1:
                res = l_i

            if abs(target[1] - other_line[1]) < abs(target[1] - lines[res][1]):
                res = l_i

        return res

    @staticmethod
    def cut_line(lines):
        # 取出x的斷點
        location_x = []
        for line in lines:
            for i in range(2):
                l = 0
                for x in location_x:
                    if x < (line[i * 2] + i):
                        l += 1
                location_x.insert(l, line[i * 2] + i)
        # print(location_x)
        res = []
        for line in lines:
            # 使用斷點對線段進行分割
            cut_line = [line]
            for x in location_x:
                # 判斷斷點是否對此線段有效 有則分割
                if (cut_line[-1][0] < x) and (cut_line[-1][2] >= x):
                    cuting = cut_line.pop(-1)

                    def get_new_y(x, line):
                        x_scale = (line[2] - line[0])
                        y_scale = (line[3] - line[1])

                        per = (x - line[0]) / x_scale
                        return int(per * y_scale) + line[1]

                    left = [cuting[0], cuting[1], x - 1, get_new_y(x - 1, cuting)]
                    right = [x, get_new_y(x, cuting), cuting[2], cuting[3]]
                    cut_line.append(left)
                    cut_line.append(right)
            res.extend(cut_line)
        # 找出重複範圍的線段進行合併
        reg = []
        for l_1 in res:
            for l_2 in res:
                if l_1 == l_2:
                    continue
                if (l_1[0] == l_2[0]) and (l_1[2] == l_2[2]):
                    if l_1[1] > l_2[1]:
                        reg = [l_2, l_1]
                    else:
                        reg = [l_1, l_2]
                    res.remove(l_1)
                    res.remove(l_2)

        return reg, res

    def get_regions(self, lines: list):
            print("Starting Cutting")
            regions = []
            # 重複切割 合併線條 直到所有線條合併完成
            while lines:
                print(len(lines))
                # 取出線段的資訊
                line = lines.pop(0)

                # 找到離自己最近的線段
                closest_index = self.find_closest_line(lines, line)
                if closest_index == -1:
                    print("funk")
                closest_line = lines.pop(closest_index)

                # 將兩線段進行分割
                new_region, cut_lines = self.cut_line([closest_line, line])

                lines.extend(cut_lines)

                regions.append(new_region)
            return regions


    def get_map(self):
        res = self.map.copy()
        regions_black = [r for r in self.regions if r not in self.path]
        for i in regions_black:
            for x in range(i[2]):
                for y in range(i[3]):
                    res[i[1] + y][i[0] + x] = 1
        return res