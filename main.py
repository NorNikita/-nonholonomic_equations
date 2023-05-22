# import Dynamics
# if __name__ == "__main__":
#     Dynamics.print_equations_for_Wolfram_Mathematica()
import time

# import numpy
# from aesara import pp
# t = at.dscalar('t')
# x = aesara.function([t], )
# y = x ** 2
# gy = at.grad(y, x)
# pp(gy)  # print out the gradient prior to optimization
# '((fill((x ** TensorConstant{2}), TensorConstant{1.0}) * TensorConstant{2}) * (x ** (TensorConstant{2} - TensorConstant{1})))'
# f = aesara.function([x], gy)
#
# t = f.grad(x)

import sympy
import tqdm
from sympy import *
import symengine as se
from definitions.generic_coordinates import *
from definitions.constants import *
from definitions.coefficient_for_resolve import *
from definitions.moments import *
from utils.common import remove_current_and_above_smallness_from_one_term, \
    remove_required_and_above_smallness_from_expression, simplification_expression, \
    expand_and_collect_term_before_derivatives_and_lambda, simplify_determinant

from utils.sympy_expression import parse_2_sympy_expression
from utils.to_sympy_expression import transform_to_simpy

g = 10
det = 4.17168745191651e-15
eq1 = (8.57439302156898e-17*g*x1 - 5.03866441343397e-16*g*x3 - 8.57439302156898e-17*g*x6)/det
eq2 = (5.30789368236859e-16*g*x2 - 8.30693292181823e-17*g)/det #-8.30693292181823e-17*g*x1 + 5.30789368236859e-16*g*x2 + 8.30693292181823e-17*g*x6
eq3 = (6.40577706714846e-15*g*x3)/det
eq4 = (1.11279732907562e-15*g*x1 + 5.73840616864587e-14*g*x3 - 1.11279732907562e-15*g*x6)/det
eq5 = -0.0039*g*x2


print("eq1 = ", transform_to_simpy(str(eq1)))
print("eq2 = ", transform_to_simpy(str(eq2)))
print("eq3 = ", transform_to_simpy(str(eq3)))
print("eq4 = ", transform_to_simpy(str(eq4)), "\n")
# print("eq6 = ", transform_to_simpy(str(eq6)))

det = 2.97583499009185e-9

eq1 = (-4.24780545990133e-11 * g * x3 - 7.01616647090093e-12 * g) / det  # x
eq2 = (4.25377957649214e-11 * g * x2 - 7.02456252665018e-12 * g) / det  # y
eq3 = (5.22099390050843e-10 * g * x2 + 5.22173464652093e-10 * g * x3) / det  # α
eq4 = -0.0039 * g * x2 - 0.0039 * g * x3  # δ

print("eq1 = ", transform_to_simpy(str(eq1)))
print("eq2 = ", transform_to_simpy(str(eq2)))
print("eq3 = ", transform_to_simpy(str(eq3)))
print("eq4 = ", transform_to_simpy(str(eq4)))
x20_value = 0.207
x30_value = 0.21

inertia = {
    J_px: M_p * R_p ** 2 / 4 + M_p * C_Mz ** 2,
    J_py: M_p * R_p ** 2 / 4 + M_p * C_Mz ** 2,
    J_pz: M_p * R_p ** 2 / 4,
    J_wx: m * r ** 2 / 4 + m * C_mz ** 2,
    J_wy: m * r ** 2 / 2 + m * C_mz ** 2,
    J_wz: m * r ** 2 / 4
}

param_dict = {
    C_mz: (0.081 - 0.026),
    C_Mz: 0.01,
    C_Mx: 0.003,
    C_My: 0.0005,

    g: 10,
    R: 0.081,
    r: 0.026,
    m: 0.05,
    M: 0.137,
    M_p: 0.65,
    R_p: 0.08,

    x20: x20_value,
    x30: x30_value
}

a_x, a_y, a_a, a_ph, a_ps, a_del = symbols("a_x, a_y, a_a, a_ph, a_ps, a_del")


mixed_coeff_eq5 = {
    a_del: parse_2_sympy_expression(open(
        "./collect_parallel/eq8/d_d_δ_t__2__.txt").readline()).coeff(diff(diff(x6, t), t)).subs(inertia).subs(param_dict, simultaneous=True),

    a_x: parse_2_sympy_expression(open(
        "./collect_parallel/eq8/d_d_x_t__2__.txt").readline()).coeff(diff(diff(x, t), t)).subs(inertia).subs(param_dict, simultaneous=True),
    a_y: parse_2_sympy_expression(open(
        "./collect_parallel/eq8/d_d_y_t__2__.txt").readline()).coeff(diff(diff(y, t), t)).subs(inertia).subs(param_dict, simultaneous=True),
    a_a: parse_2_sympy_expression(open(
        "./collect_parallel/eq8/d_d_α_t__2__.txt").readline()).coeff(diff(diff(x1, t), t)).subs(inertia).subs(param_dict, simultaneous=True),
    a_ph: parse_2_sympy_expression(open(
        "./collect_parallel/eq8/d_d_φ_t__2__.txt").readline()).coeff(diff(diff(x4, t), t)).subs(inertia).subs(param_dict, simultaneous=True),
    a_ps: parse_2_sympy_expression(open(
        "./collect_parallel/eq8/d_d_ψ_t__2__.txt").readline()).coeff(diff(diff(x5, t), t)).subs(inertia).subs(param_dict, simultaneous=True),
    free_7: -parse_2_sympy_expression(open(
        "./collect_parallel/eq8/free_term.txt").readline()).subs(inertia).subs(param_dict),
}

eq5 = (free_7 - a_x * eq1 - a_y * eq2 - a_a * eq3 - a_ph * eq4 - a_ps * eq6)/a_del
eq5 = eq5.subs(mixed_coeff_eq5)

print("eq5 = ", transform_to_simpy(str(eq5)))

# aa1 = parse_2_sympy_expression(open("./collect_parallel/eq6/d_d_x_t__2__.txt").readline()).coeff(diff(diff(x, t), t))
# aa2 = parse_2_sympy_expression(open("./collect_parallel/eq6/d_d_φ_t__2__.txt").readline()).coeff(diff(diff(x4, t), t))
# free1 = (parse_2_sympy_expression(open("./collect_parallel/eq6/free_term.txt").readline()).coeff(x3))
#
# bb1 = (parse_2_sympy_expression(open("./collect_parallel/eq10/d_d_x_t__2__.txt").readline()) / 3).coeff(diff(diff(x, t), t))
# bb2 = (parse_2_sympy_expression(open("./collect_parallel/eq10/d_d_φ_t__2__.txt").readline()) / 3).coeff(diff(diff(x4, t), t))
# free2 = (parse_2_sympy_expression(open("./collect_parallel/eq10/free_term.txt").readline()).coeff(x3)) / 3
#
# A = Matrix([[aa1, aa2], [bb1, bb2]])
# Free = -Matrix([[free1], [free2]])
#
# det = simplify(A.det())
# print(print_in_latex(det))
#
# Free = A.inv() * Free
# top1, _ = fraction(together(Free.row(0)[0]))
# top2, _ = fraction(together(Free.row(1)[0]))
# print(print_in_latex(simplify(top1)))
# print(print_in_latex(simplify(top2)))
#
# inertia = {
#     J_px: M_p * R_p ** 2 / 4 + M_p * C_Mz ** 2,
#     J_py: M_p * R_p ** 2 / 4 + M_p * C_Mz ** 2,
#     J_pz: M_p * R_p ** 2 / 4,
#     J_wx: m * r ** 2 / 4 + m * C_mz ** 2,
#     J_wy: m * r ** 2 / 2 + m * C_mz ** 2,
#     J_wz: m * r ** 2 / 4
# }
#
# param_dict = {
#     C_mz: (0.081 - 0.026),
#     C_Mz: 0.01,
#
#     g: 10,
#     R: 0.081,
#     r: 0.026,
#     m: 0.05,
#     M: 0.137,
#     M_p: 0.65,
#     R_p: 0.08
# }
# det = det.subs(inertia).subs(param_dict)
# print(det)
#
# top1 = Free.row(0)[0].subs(inertia).subs(param_dict)
# print(top1)
# top2 = Free.row(1)[0].subs(inertia).subs(param_dict)
# print(top2)
#
# coeff_y = parse_2_sympy_expression(open("./collect_parallel/eq9/d_d_y_t__2__.txt").readline()).coeff(diff(diff(y, t), t)).subs(inertia).subs(param_dict)
# coeff_free = - parse_2_sympy_expression(open("./collect_parallel/eq9/free_term.txt").readline()).coeff(x2).subs(inertia).subs(param_dict)
# print("y coeff = ", coeff_free/coeff_y)