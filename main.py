import os
from A_star import Astar
import cv2
import numpy as np
from graph import CellDec

EMPTY_CELL = 0
OBSTACLE_CELL = 1
START_CELL = 2
GOAL_CELL = 3
white = np.array([255, 255, 255])
black = np.array([0, 0, 0])
red = np.array([36, 28, 237])
yellow = np.array([0, 242, 255])


def gen_map(file):
    img = cv2.imread(os.path.join(os.getcwd(), 'maps_img', file), cv2.IMREAD_COLOR)
    data = np.zeros([img.shape[1], img.shape[0]])
    for i in range(img.shape[1]):
        for j in range(img.shape[0]):
            if (img[i, j] == white).all():
                data[i, j] = EMPTY_CELL
            elif (img[i, j] == black).all():
                data[i, j] = OBSTACLE_CELL
            elif (img[i, j] == red).all():
                data[i, j] = START_CELL
            elif (img[i, j] == yellow).all():
                data[i, j] = GOAL_CELL

    np.savetxt(os.path.join(os.getcwd(), 'maps_csv', file[:-4] + '.csv'), data, delimiter=',', fmt='%d')

def get_point(map, val: int):
    for y in range(map.shape[0]):
        for x in range(map.shape[1]):
            if map[y, x] == val:
                return x, y


def preprocessing(img, e, s):
    img[s.y, s.x] = 0
    img[e.y, e.x] = 0
    return img


def main(maps):
    for i in maps:
        print('initial searching on ' + i[:-4])
        map = np.genfromtxt(os.path.join(os.getcwd(), 'maps_csv', i), delimiter=',')
        e_point = get_point(map, 3)
        now_on = get_point(map, 2)
        a = Astar(now_on, e_point, map, i)
        cell = CellDec(map)
        lines = cell.getLines()
        regions = cell.get_regions(lines)

        cell.draw(i, regions, '_cu')

        cell.gen_graph(regions)
        regs = cell.search(now_on, e_point)

        # cell.draw(i[:-4] + '.png', regs, '_se')

        a.close_set = cell.get_map()
        a.setting(regs)
        print('start searching on ' + i[:-4])
        print(a.search())
        print('Done searching on ' + i[:-4])


maps = os.listdir(os.path.join(os.getcwd(), 'maps_csv'))
main(['small-hard.csv'])
# gen_map('test.png')