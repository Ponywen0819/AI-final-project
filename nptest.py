import numpy as np
import cv2

black = np.array([0, 0, 0])
a = cv2.imread('./maps/small-easy.png')
print(a)
map = np.full((a.shape[1], a.shape[0], 3), black)

print(map.shape)