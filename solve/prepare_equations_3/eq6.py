from main_file import *

mixed_coeff_eq6 = {
    free_7: -parse_2_sympy_expression(open(
        "../../collect_parallel/eq7/free_term.txt").readline()).subs(inertia).subs(param_dict),
}
eq7 = eq7.subs(mixed_coeff_eq6)
with open("eqns/eq6.txt", "w") as out:
    out.write(transform_to_simpy(str(eq7)))
print("prepared eq6")
