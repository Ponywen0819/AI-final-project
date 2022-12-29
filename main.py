import os
from A_star import Astar
import cv2
import numpy as np
from graph import CellDec
from ccpp import CCPP
import collections
from spp import SPP
import time



def get_point(map, val: int):
    for y in range(map.shape[0]):
        for x in range(map.shape[1]):
            if map[y, x] == val:
                return x, y

def shortest_path(start, end, map, file):
    # a = Astar(start, end, map, file)
    # cell = CellDec(map)
    # lines = cell.getLines()
    # regions = cell.get_regions(lines)
    #
    # cell.draw(file, regions, '_cu')
    #
    # cell.gen_graph(regions)
    # regs = cell.search(start, end)
    #
    # # cell.draw(i[:-4] + '.png', regs, '_se')
    #
    # a.close_set = cell.get_map()
    # a.setting(regs)
    # print('start searching on ' + file[:-4])
    # print(a.search())
    # print('Done searching on ' + file[:-4])

    t_start = time.process_time()
    spp = SPP(start, end, map, file)
    spp.search()
    t_end = time.process_time()
    print("總布數: %d" % spp.step)
    print("總旋轉次數: %d" % spp.spin)
    print("總時長: %.2fs" % (t_end - t_start))


def complete_coverage_path(start, map, file):
    t_start = time.process_time()
    ccpp = CCPP(start, map, file)
    ccpp.coverage()
    ccpp.back_home()
    t_end = time.process_time()
    print("總布數: %d" % ccpp.step)
    print("總旋轉次數: %d" % ccpp.spin)
    ccpp.get_can_reached()
    print("可覆蓋面積: %d" % ccpp.can_reach)
    print("已覆蓋面積: %d" % np.count_nonzero(ccpp.reached))
    print("覆蓋度: %.2f" % (np.count_nonzero(ccpp.reached) / ccpp.can_reach))
    print("總時長: %.2fs" % (t_end - t_start))

def main(maps):
    for i in maps:
        if i[-3:] == 'csv':
            print('--------------------------------------------------')
            print('proccessing on ' + i[:-4])
            print('--------------------------------------------------')
            map = np.genfromtxt(os.path.join(os.getcwd(), 'maps_csv', i), delimiter=',', dtype=int)
            end = get_point(map, 3)
            start = get_point(map, 2)

            print("Start finding shortest path")
            shortest_path(start, end, map, i[:-4])

            print("Start finding complete coverage path")
            complete_coverage_path(start, map, i[:-4])


maps = os.listdir(os.path.join(os.getcwd(), 'maps_csv'))
main(maps)