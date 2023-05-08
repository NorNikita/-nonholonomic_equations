from utils.common import *
from Kinematics import *
from definitions.moments import *
from definitions.lagrangian_multipliers import *
import time
from sympy.solvers.solveset import linsolve, linear_eq_to_matrix, solveset, nonlinsolve
from utils.Wolfram import Wolfram
from utils.to_sympy_expression import transform_to_simpy
from sympy import expand, sqrt, S
from utils.latex_converter import print_in_latex
from math import asin, pi

# TODO создать функцию, которая будет это высчитывать и подставлять в common.py

vector_R = Matrix([[0], [0], [-R]])
mom_g_platform = (P_x_X * R_cm_p - vector_R).cross(Matrix([[0], [0], [-M_p * g]]))
mom_g_wheel = (P_x_X * R_cm_w - vector_R).cross(Matrix([[0], [0], [-m * g]]))

sum_of_moment = mom_g_wheel + mom_g_platform


def get_gamma_when_C_Mx_non_zero(C_Mx, C_Mz, C_mz, M_p, m, k=0):
    d = C_Mx**2 * M_p**2 + (C_mz * m + C_Mz * M_p)**2
    gamma_ = asin(C_Mx * M_p / sqrt(d)) + pi * (k - 1)
    return gamma_

eq1 = trigsimp(sum_of_moment[0].subs({x1: 0, x2: 0}))
print("eq1 = ", eq1)
eq2 = trigsimp(sum_of_moment[1].subs({x1: 0, x2: 0}))
print("eq2 = ", eq2)
dict_eq = {
    C_mz: (0.081 - 0.026),
    C_Mz: 0.01,
    C_Mx: 0.002,
    C_My: 0.002,
    m: 0.05,
    g: 10,
    M_p: 0.65}
system = [eq1.subs(dict_eq), eq2.subs(dict_eq)]
print(solveset(eq2.subs(dict_eq), x3, domain=S.Reals))
values = nonlinsolve(system, [x2, x3])
print(values)


expr_asin = C_Mx*M_p/sqrt(C_Mx**2 * M_p**2 + (m * C_mz + C_Mz * M_p)**2)
expr_asin = expr_asin.subs(dict_eq)
gamma = asin(expr_asin)
print("gamma [rad] = ", gamma)
print("gamma [angle] = ", gamma * 180 / 3.14)

eq1 = expand(eq1.subs(dict_eq))
eq1 = eq1.subs({x3: gamma})
print(eq1)
beta = 0.21 # rad
print("beta [rad] = ", beta)
print("beta [angle] = ", beta * 180 / 3.14)

gamma_ = get_gamma_when_C_Mx_non_zero(0.002, -0.01, -0.055, 0.65, 0.05, k=1)
print("When only C_Mx offset. GAMMA [rad] = ", gamma_)
print("When only C_Mx offset. GAMMA [deg] = ", gamma_ * 180/3.14)
