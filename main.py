import os
import pandas as pd
from Point import Point
from A_star import A_star
import cv2
import numpy as np

white = np.array([255, 255, 255])
black = np.array([0, 0, 0])


def get_point(map, type):
    for y in range(map.shape[0]):
        for x in range(map.shape[1]):
            if (map[y, x] == type).all():
                return x, y


def main(maps):
    red = np.array([36, 28, 237])
    yellow = np.array([0, 242, 255])
    for i in maps:
        print('initial searching on ' + i[:-4])
        img = cv2.imread(os.path.join(os.getcwd(), 'maps', i), cv2.IMREAD_COLOR)
        e_point = Point(get_point(img, yellow), None, None, 0)
        now_on = Point(get_point(img, red), None, e_point, 0)
        print('start searching on ' + i[:-4])
        a = A_star(img, now_on, e_point)
        a.search()
        print('Done searching on ' + i[:-4])
        a.get_path(i)


maps = os.listdir(os.path.join(os.getcwd(), 'maps'))
# main( ['medium-medium.png' ])

#
# a = [1,2,3,4,5]
# #
# a.sort()
# print(a)