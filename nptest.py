import cv2
import math


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
            if (cut_line[-1][0] < x) and (cut_line[-1][2] > x):
                cuting = cut_line.pop(-1)

                def get_new_y(x, line):
                    x_scale = (line[2] - line[0])
                    y_scale = (line[3] - line[1])

                    per = (x - line[0]) / x_scale
                    return int(per * y_scale) + line[1]
                left = [cuting[0], cuting[1], x - 1,  get_new_y(x - 1, cuting)]
                right = [x, get_new_y(x, cuting), cuting[2], cuting[3]]
                cut_line.append(left)
                cut_line.append(right)
        res.extend(cut_line)
    return res

a = [[20, 1, 80, 3], [15, 10, 60, 8]]
print(cut_line(a))
# print(a.pop(-1))
