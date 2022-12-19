import cv2
import os
import numpy as np

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
