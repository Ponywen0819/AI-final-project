import cv2.cv2 as cv2
import numpy as np
from region import Region


class Line:

    def __init__(self, x, y, l):
        self.x = x
        self.y = y
        self.l = l


class Div:
    def __init__(self, map):
        self.map = map  # 載入地圖原始資料
        self.res = []  # 切分地圖結果
        self.graph = []  # 圖片中的圖形
    @staticmethod
    def check_homogeneous(r: Region):
        sample = r.map[0, 0]
        return np.all(sample == r.map)

    @staticmethod
    def cut(r: Region):
        x, y, w, h = r.get_info()

        cut = []

        half_w = w // 2
        half_h = h // 2

        for i in range(2):
            for j in range(2):
                index_x = half_w * i
                index_y = half_h * j

                new_x = x + index_x
                new_y = y + index_y

                temp = Region(r.map[index_y: index_y + half_h, index_x: index_x + half_w], new_x, new_y)
                cut.append(temp)
        for i in cut:
            for j in cut:
                if i is not j:
                    i.add_near(j)
        return cut

    @staticmethod
    def check_near(a: Region,b: Region):
        a_x, a_y, a_w, a_h = a.get_info()
        b_x, b_y, b_w, b_h = b.get_info()

        a_middle_x = a_x + a_w // 2
        a_middle_y = a_y + a_h // 2

        b_middle_x = b_x + b_w // 2
        b_middle_y = b_y + b_h // 2

        diff_x = abs(a_middle_x - b_middle_x)
        diff_y = abs(a_middle_y - b_middle_y)

        is_x_in_range = diff_x <= (a_w + b_w)
        is_y_in_range = diff_y <= (a_h + b_h)

        return is_x_in_range and is_y_in_range

    def dividing(self, r: Region):
        pass

    def get_line(self):
        pass

    def get_black_graph(self):
        open = []
        closed =[]
        x, y =(0, 0)
        while x < self.map.shape[1]:
            if np.all(self.map[:, x] == np.array(255, 255, 255)):
                while y < self.map.shape[0]:


    def start_div(self):
        # 將地圖初始化到list中
        initial_region = Region(self.map, 0, 0)
        self.dividing(initial_region)


# img = cv2.imread('./maps/small-easy.png')
#
# # 初始步驟
# process = Div(img)
#
# process.start_div()
#
# ans = process.get_ans()
#
# print(len(ans))
