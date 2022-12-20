import os
from A_star import Astar
import cv2
import numpy as np
from graph import CellDec
from ccpp import CCPP



def get_point(map, val: int):
    for y in range(map.shape[0]):
        for x in range(map.shape[1]):
            if map[y, x] == val:
                return x, y

def shortest_path(start, end, map, file):
    a = Astar(start, end, map, file)
    cell = CellDec(map)
    lines = cell.getLines()
    regions = cell.get_regions(lines)

    cell.draw(file, regions, '_cu')

    cell.gen_graph(regions)
    regs = cell.search(start, end)

    # cell.draw(i[:-4] + '.png', regs, '_se')

    a.close_set = cell.get_map()
    a.setting(regs)
    print('start searching on ' + file[:-4])
    print(a.search())
    print('Done searching on ' + file[:-4])

def complete_coverage_path(start, map, file):
    ccpp = CCPP(start, map)
    ccpp.Coverage()
    ccpp.back_home()
def main(maps):
    for i in maps:
        print('proccessing on ' + i[:-4])
        map = np.genfromtxt(os.path.join(os.getcwd(), 'maps_csv', i), delimiter=',', dtype=int)
        end = get_point(map, 3)
        start = get_point(map, 2)

        # print("Start finding shortest path")
        # shortest_path(start, end,map , i)

        print("Start finding complete coverage path")
        complete_coverage_path(start, map, i)


maps = os.listdir(os.path.join(os.getcwd(), 'maps_csv'))
main(['small-hard.csv'])
# gen_map('test.png')