import numpy as np
import cv2
import os
from rolling import rolling
SIZE = 10


def get_distance(x_1, y_1, x_2, y_2):
    return ((x_1 - x_2) ** 2 + (y_1 - y_2) ** 2) ** 0.5


def enlarge_circle(c_x, c_y, map):
    y, x = np.ogrid[0:map.shape[0], 0:map.shape[0]]

    mask = (x - c_x) ** 2 + (y - c_y) ** 2 <= SIZE ** 2

    map[mask] = 1

def map_enlarge(map):
    print('Start enlarge map')
    rolling_sign = rolling()
    # 用於存放障礙物放大後的地圖
    res = np.copy(map)
    # 遍歷全部的節點
    for y in range(map.shape[0]):
        for x in range(map.shape[1]):
            next(rolling_sign)
            if map[y, x] == 0:
                continue
            if (map[y, x] == 2) or (map[y, x] == 3):
                res[y, x] = 0
                continue
            # 檢查是否是障礙物邊緣
            is_edge = False
            for i, j in [(0, 1), (1, 0), (-1, 0), (0, -1)]:
                next_x = x + i
                next_y = y + j
                if (next_y < 0) or (next_y > (map.shape[0] - 1)):
                    continue
                if (next_x < 0) or (next_x > (map.shape[1] - 1)):
                    continue
                if int(map[next_y, next_x]) == 0:
                    is_edge = True
            if not is_edge:
                continue
            enlarge_circle(x, y, res)
    # 地圖邊緣膨脹
    for y in range(map.shape[0]):
        next(rolling_sign)
        # 篩選掉不必要的節點
        enlarge_circle(-1, y, res)
        enlarge_circle(map.shape[1], y, res)
    for x in range(map.shape[1]):
        next(rolling_sign)
        # 篩選掉不必要的節點
        enlarge_circle(x, -1, res)
        enlarge_circle(x, map.shape[0], res)
    img = cv2.imread('maps_img/small-hard.png')
    for x in range(img.shape[1]):
        for y in range(img.shape[0]):
            img[y, x] = np.array([255, 255, 255] if res[y, x] == 0 else [0, 0, 0])
    cv2.imwrite('res/small-hard-large.png', img)

    return res