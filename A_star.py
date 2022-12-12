from Point import Point
import math
import cv2
import numpy as np
import os
SIZE = 10

class A_star:
    def __init__(self, map, start: Point, end: Point):
        self.map = map
        self.start = start
        self.end = end
        self.left = []
        self.ans = None
        self.closed = []
    def check_move(self, degree, p:Point):
        '''
        確認操作是否合法
        :return:
        '''

        # 將角度轉換到實際操作
        index_x = 0
        index_y = 0
        if (degree < 90) or (degree > 270):
            index_y = 1
        elif (degree == 90) or (degree == 270):
            index_y = 0
        else:
            index_y = -1

        if (degree > 0) and (degree < 180):
            index_x = 1
        elif (degree == 180) or (degree == 0):
            index_x = 0
        else:
            index_x = -1
        # 檢查碰撞

        for i in range(0, 360, 10):
            temp_x = p.x + index_x + int(SIZE * math.sin(i))
            temp_y = p.y + index_y + int(SIZE * math.cos(i))
            if (temp_y >= self.map.shape[0]) or (temp_x >= self.map.shape[1]):
                return  None
            elif (self.map[temp_y, temp_x] == np.array([0, 0, 0])).all():
                return None
        return p.x + index_x, p.y + index_y

    def append(self, p: Point):
        '''
        將節點之子節點展開
        '''

        if p in self.closed:
            return
        # 逐一檢查合法節點
        for i in range(0, 360, 45):
            vaild_move = self.check_move(i, p)
            if vaild_move is not None:
                self.left.insert(0, Point(vaild_move, p, self.end, i))
        # 將葉節點根據cost func進行排序
        self.left.sort(key=lambda x: x.get_cost_func())

    def get_path(self,filename):
        temp = self.ans
        ans_map = self.map
        ans = []
        while temp.parent is not None:
            temp_x = temp.x
            temp_y = temp.y
            for i in range(temp_y-5,temp_y+4):
                for j in range(temp_x-5, temp_x+4):
                    ans_map[i, j] = np.array([255, 0, 0])
            parent = temp.parent

            # 依據角度來重建路徑
            if parent.degree == temp.degree:
                ans.append(0)  # 插入前進
            elif abs(parent.degree - temp.degree) == 180:
                ans.append(1)  # 插入後退
            else:
                ans.append(0)
                ans.append(2)  # 插入旋轉
            temp = parent

        cv2.imwrite(os.path.join(os.getcwd(), 'res', filename), ans_map)
        ans.reverse()


        return ans

    def search(self) -> None:
        '''
            開始尋找路徑
            :return:
            none
        '''
        self.left.append(self.start)
        # 初始化結束
        max_node = self.map.shape[0] * self.map.shape[1]

        while len(self.left) <= max_node:
            # 將第一優先的節點取出
            temp_p = self.left.pop(0)
            # print(temp_p)
            # 將結點展開
            if temp_p == self.end:
                self.ans = temp_p
                return
            self.append(temp_p)
            self.closed.append(temp_p)

