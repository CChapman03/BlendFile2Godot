import os
import sys
import numpy as np
import math as m
import random

class Math_Utilities():

    def __init__(self):
        pass

    def Rx(self, angle):
        return np.matrix([[1.0, 0.0,          0.0],
                        [0.0, m.cos(angle), -m.sin(angle)],
                        [0.0, m.sin(angle), m.cos(angle)]])

    def Ry(self, angle):
        return np.matrix([[m.cos(angle), 0.0, m.sin(angle)],
                        [0.0,          1.0, 0.0],
                        [-m.sin(angle), 0.0, m.cos(angle)]])
    def Rz(self, angle):
        return np.matrix([[m.cos(angle), 0.0, -m.sin(angle)],
                        [m.sin(angle), m.cos(angle), 0.0],
                        [0.0,          0.0,          1.0]])

    def R(self, angle_x, angle_y, angle_z):
        rx = self.Rx(angle_x)
        ry = self.Ry(angle_y)
        rz = self.Rz(angle_z)

        r = rz * ry * rx

        return r

    def S(self, scale):
        return np.matrix([[scale, 0.0,   0.0],
                        [0.0,   scale, 0.0],
                        [0.0,   0.0,   scale]])

    def S3D(self, scale_x, scale_y, scale_z):
        return np.matrix([[scale_x, 0.0,   0.0],
                        [0.0,   scale_y, 0.0],
                        [0.0,   0.0,   scale_z]])

    def T(self, x, y, z):
        return [x, y, z]

    def ID(self):
        return np.matrix( [ [1, 0, 0, 0],
                            [0, 1, 0, 0],
                            [0, 0, 1, 0],
                            [0, 0, 0, 1] ])

    def to_array(self, mat):
        return np.squeeze(np.asarray(mat))

    def transform(self, R, S, T):

        rs = R * S

        rs_array = self.to_array(rs)

        trans = [rs_array[0][0], rs_array[0][1], rs_array[0][2],
                 rs_array[1][0], rs_array[1][1], rs_array[1][2],
                 rs_array[2][0], rs_array[2][1], rs_array[2][2],
                 T[0], T[1], T[2]]

        return trans

    def to_str(self, array):
        str_array = []

        for item in array:
            str_array += [str(item)]

        return str_array