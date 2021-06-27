import numpy as np
import math

"""
基于平面几何的姿态识别
"""

class UTIL:
    def initialization(self, array):
        """单位化一个向量"""
        return array / math.sqrt(np.sum(np.square(array)))

    def cal_cos(self, array_a, array_b):
        """计算向量夹角"""
        return np.dot(array_a,array_b) / math.sqrt(np.sum(np.square(array_a)) * np.sum(np.square(array_b)))


class POSTRECOGNIZE:
    def __init__(self, humans_time):
        #
        self.util = UTIL()
        # 分离人
        self.num = 0
        self.humans = []
        self.separateHuman(humans_time)
        #

    def separateHuman(self, all_humans):
        """分离人"""
        # 获取总共多少人
        self.num = len(all_humans[0])
        # 将self.huams变为n维
        for i in range(self.num):
            self.humans.append([])
        # 分离人
        for humans in all_humans:
            for index, human in enumerate(humans):
                if index >= self.num:
                    break
                self.humans[index].append(human)

    def recognize(self, human):
        """识别单个人"""
        ans = ''
        # 识别抬手
        ans += self.recognize_taishou(human)
        # 返回结果
        return ans

    def recognize_taishou(self, human):
        ans = ''
        # 计算各组向量
        vector_r = []
        vector_l = []
        vector_r_trend = []
        vector_l_trend = []
        for index,value in enumerate(human):
            keys = value.body_parts.keys()
            if 2 in keys and 3 in keys and 4 in keys:
                point_root = np.array([value.body_parts[2].x, value.body_parts[2].y])
                point_a = np.array([value.body_parts[3].x, value.body_parts[3].y])
                point_b = np.array([value.body_parts[4].x, value.body_parts[4].y])
                # 计算向量臂差的模
                vector_a = self.util.initialization(point_a - point_root)
                vector_b = self.util.initialization(point_b - point_root)
                # _vector = vector_b -vector_a
                # _vector = math.sqrt(np.sum(_vector * _vector))
                vector_r.append(self.util.cal_cos(vector_a, vector_b))
                # 计算向量臂趋势
                _vector = self.util.initialization((point_a-point_root)+(point_b-point_root))
                vector_r_trend.append(self.util.cal_cos(_vector, np.array([1,0])))
            if 5 in keys and 6 in keys and 7 in keys:
                point_root = np.array([value.body_parts[5].x, value.body_parts[5].y])
                point_a = np.array([value.body_parts[6].x, value.body_parts[6].y])
                point_b = np.array([value.body_parts[7].x, value.body_parts[7].y])
                # 计算向量臂差的模
                vector_a = self.util.initialization(point_a - point_root)
                vector_b = self.util.initialization(point_b - point_root)
                # _vector = vector_b -vector_a
                # _vector = math.sqrt(np.sum(_vector * _vector))
                vector_l.append(self.util.cal_cos(vector_a, vector_b))
                # 计算向量臂趋势
                _vector = self.util.initialization((point_a - point_root) + (point_b - point_root))
                vector_l_trend.append(self.util.cal_cos(_vector, np.array([1, 0])))
        # 计算
        if len(vector_r) != 0 and len(vector_r_trend) != 0:
            if self.recognize_taishou_part(vector_r, vector_r_trend):
                ans += '抬右手 '
        if len(vector_l) != 0 and len(vector_l_trend) != 0:
            if self.recognize_taishou_part(vector_l, vector_l_trend):
                ans += '抬左手 '
        return ans


    def recognize_taishou_part(self, vector, vector_trend):
        # 计算向量臂夹角是否足够小
        vector = np.array(vector)
        flg_1 = False
        if np.mean(vector) > 0.6:
            flg_1 = True
        # for item in vector:
        #     if item < 0.2:
        #         flg_1 = True
        #         break
        # 计算方向是否小
        flg_2 = False
        vector_trend = np.array(vector_trend)
        if np.mean(vector_trend[vector_trend>=0]) > 0.6 or np.mean(vector_trend[vector_trend<=0]) < -0.6:
            flg_2 = True
        # for item in vector_trend:
        #     cos = self.util.cal_cos(item, np.array([0,1]))
        #     print(cos)
        #     if cos > 0.85 or cos < -0.85:
        #         flg_2 = True
        #         break
        print(np.mean(vector), np.mean(vector_trend[vector_trend>=0]), np.mean(vector_trend[vector_trend<=0]))
        return flg_1 and flg_2

    def run(self):
        """入口函数"""
        ans = []
        # 初始化结果集
        for i in range(self.num):
            ans.append('第'+str(i)+'个人:')
        # 分人识别
        for index,human in enumerate(self.humans):
            ans[index] += self.recognize(human)
        return ans


if __name__ == '__main__':
    POSTRECOGNIZE()