from main_file import *
import sys
sys.setrecursionlimit(10000000)

mixed_coeff_eq4 = {
    free_4: parse_2_sympy_expression(open("../../resolve_second_diff/part3_1/free_3_0.txt").readline()).subs(inertia).subs(param_dict)
}
eq4 = eq4.subs(mixed_coeff_eq4)
with open("eqns/eq4.txt", "w") as out:
    out.write(transform_to_simpy(str(eq4)))
print("prepared eq4")