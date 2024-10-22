import math
import random

import numpy as np
from Tools.scripts.make_ctype import values
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, url_for, redirect
from app import str2float

# keys = ["BPn", "BPk", "MPn", "MPk", "BV", "BC", "BZ", "MV", "MC", "MZ",
#         "C", "P", "PT", "PI", "PJ", "PD", "PS", "G", "IG", "NG", "F",
#         "An", "Ak", "Vn", "Vk", "IDPn", "IDPk", "DPn", "DPk", "IB",
#         "IN", "IL", "DS", "DV", "DP", "JDn", "JDk", "INn", "INk", "NPP",
#         "PPn", "PPk", "OKDNPR", "OKD", "PBn", "PBk", "PB", "PMn", "PMk", "PM", "IPn", "IPk",
#         "OPn", "OPk", "JPn", "JPk", "ISPn", "ISPk", "BRPn", "BRPk",
#         "MRPn", "MRPk", "SRPn", "SRPk", "RPn", "RPk", "IR", "NR"]
keys = ["L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8", "L9", "L10", "L11", "L12", "L13", "L14", "L15"]

map = {}
# for key in keys:
#     map[key] = 0.
# map[key] = 1.4
f_ind = [[]]
q_ind = [[]]


def f(i, x):
    a, b, c, d = f_ind[i-1]  # Теперь d тоже учитывается
    return a + b * x + c * x ** 2 + d * x ** 3  # Кубическая функция

def q(i, x):
    a, b, c, d = q_ind[i-1]  # Теперь d тоже учитывается
    # return a + b * np.sin(c * x + d) # Кубическая функция
    return a + b * x + c * x ** 2 + d * x ** 3
# def q2(i, x):
#     a, b, c, d = f_ind[i-1]  # Теперь d тоже учитывается
#     return a + b * np.sin(c * x + d)  # Кубическая функция
# def q3(i, x):
#     a, b, c, d = f_ind[i-1]  # Теперь d тоже учитывается
#     return a + c * x ** 2   # Кубическая функция
# def q4(i, x):
#     a, b, c, d = f_ind[i-1]  # Теперь d тоже учитывается
#     return a +  c * x ** 2  # Кубическая функция
# def q5(i, x):
#     a, b, c, d = f_ind[i-1]  # Теперь d тоже учитывается
#     return a +  c * x ** 0.5  # Кубическая функция


# Определите систему уравнений
def system(t, x):
    x = np.insert(x, 0, 0)
    dxdt = [
        (1 / map["L1"]) * (f(1, x[5]) * f(2, x[6])
                * f(3, x[7]) * f(4, x[10]) * f(5, x[13])
                * f(6, x[14]) * (q(1, x[1]) + (q(2, x[1]))) - q(3, x[1])),
        (1 / map["L2"]) * (f(7, x[3]) * f(8, x[12])
                * x[13] * f(10, x[14]) * f(11, x[15])
                * (q(1, x[2]) + q(5, x[2])) - q(4, x[2])),
        (1 / map["L3"]) * (f(17, x[14]) * f(12, x[5])
                * f(13, x[6]) * f(14, x[7]) * f(18, x[15])
                * f(15, x[10]) * f(16, x[13])
                * q(2, x[3]) - q(5, x[3])),
        (1 / map["L4"]) * (f(25, x[11]) * f(19, x[1])
               * f(20, x[5]) * f(21, x[6]) * f(22, x[7])
               * f(26, x[14]) * f(23, x[8]) * f(24, x[10]) * f(27, x[15])
               * q(2, x[4]) - f(28, x[9])),
        (1 / map["L5"]) * (f(29, x[1]) * f(30, x[6])
               * f(31, x[7]) * f(32, x[8]) * f(33, x[10])
               * f(34, x[11]) * f(35, x[13])
               * (q(1, x[5]) + q(2, x[5]) + q(3, x[5])) - f(36, x[9])),
        (1 / map["L6"]) * (f(37, x[1]) * f(38, x[3])
               * f(39, x[4]) * f(40, x[7]) * f(41, x[8])
               * (q(1, x[6]) + q(3, x[6])) - f(42, x[9])),
        (1 / map["L7"]) * (f(43, x[4]) * f(44, x[6])
               * f(45, x[13]) * f(46, x[14])
               * (q(3, x[7]) + q(4, x[7])) - f(47, x[9])),
        (1 / map["L8"]) * (f(48, x[4]) * f(49, x[6])
               * f(50, x[7]) * f(51, x[11]) * f(52, x[13]) * f(53, x[15])
               * q(3, x[8]) - (f(54, x[5]) * f(55, x[9]))),
        (1 / map["L9"]) * (f(56, x[3]) * f(57, x[6]) * (q(1, x[9]) + q(3, x[9]) + q(4, x[9]))
                           - (f(58, x[4]) * f(59, x[5]) * f(60, x[7]) * f(61, x[8])
                           * (f(62, x[10])))),
        (1 / map["L10"]) * (f(63, x[1]) * f(64, x[6])
                           * f(65, x[11]) * f(66, x[12]) * f(67, x[13]) * f(68, x[14])
                           * (q(2, x[10]) + q(5, x[10])) - f(69, x[9])),
        (1 / map["L11"]) * (f(70, x[4]) * f(71, x[6])
                            * f(72, x[8]) * f(73, x[10]) * f(74, x[13])
                            * (q(1, x[11]) + q(3, x[11])) - f(75, x[5]) * f(76, 7)),
        (1 / map["L12"]) * (f(77, x[2]) * f(78, x[3])
                            * f(79, x[4])
                            * (q(1, x[12]) + q(2, x[12]) + q(5, x[12])) - f(80, x[9])),
        (1 / map["L13"]) * (f(81, x[1]) * f(82, x[3])
                            * f(83, x[4]) * f(84, x[5]) * f(85, x[6]) * f(86, x[10]) * f(87, x[14])
                            * (q(1, x[13]) + q(2, x[13])) - q(4, x[13])),
        (1 / map["L14"]) * (f(88, x[1]) * f(89, x[7])
                            * f(90, x[10]) * f(91, x[13])
                            * (q(2, x[14]) + q(3, x[14])) - q(5, x[14])),
        (1 / map["L15"]) * (f(92, x[2]) * f(93, x[3])
                            * f(94, x[4]) * f(95, x[6]) * f(96, x[8]) * f(97, x[9]) * f(98, x[11])
                            * (q(1, x[15]) + q(2, x[15]) + q(5, x[15])) - q(3, x[15])),
    ]
    return dxdt


def solve(initial_conditions):

    t_span = (0, 2)
    t_eval = np.linspace(t_span[0], t_span[1], 100)

    return solve_ivp(system, t_span, initial_conditions, t_eval=t_eval)
