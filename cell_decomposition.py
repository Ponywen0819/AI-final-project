import cv2.cv2 as cv2
import numpy as np
from region import Region


class Div:
    def __init__(self, map):
        self.map = map  # 載入地圖原始資料

    @staticmethod
    def cut(r: Region) -> list:
        x, y, w, h = r.get_info()

        cut = []

        half_w = w / 2
        half_h = h / 2

        for i in range(2):
            for j in range(2):
                index_x = half_w * i
                index_y = half_h * j

                new_x = x + index_x
                new_y = y + index_y

                temp = Region(new_x, new_y, r.data[index_y: index_y + half_h, index_x: index_x + half_w])
                cut.append(temp)
        return cut

    @staticmethod
    def check_homogeneous(r: Region):
        x, y, w, h = r.get_info()

        # 使用此區塊中第一個色塊見立大小一樣的陣列
        sample = np.full((h, w, 3), r.data[0, 0])

        return np.all(sample, r)

    def dividing(self, r: Region):
        if(self.check_homogeneous(r)):
            calc_list = self.cut(r)
            for i in calc_list:

        else:
            return r
    def initial_div(self):
        # 將地圖初始化到list中
        initial_region = Region(0, 0,self.map)
        regions = []

        processing = initial_region




img = cv2.imread('./maps/small-easy.png')

# 初始步驟
map_region = [Region(0, 0, img.shape[1], img.shape[0])]
