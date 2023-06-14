import time

import tqdm
from sympy import cos, sin, expand, collect, Add, sympify, Mul, simplify, trigsimp, Pow, Derivative
from sympy.core.numbers import Zero, One, Integer, Number, NegativeOne

from Kinematics import size_generic_vars
from definitions.constants import C_Mz, C_mz, r, R, J_px, J_py, J_wx, J_wy, C_Mx, C_My, cos_x20, cos_x30, sin_x20,\
    sin_x30, cos_x70, sin_x70, sin_x80, cos_x80
from definitions.denominators import *
from definitions.generic_coordinates import *
from definitions.lagrangian_multipliers import *
from definitions.moments import M_φ, M_ψ
from utils.Wolfram import Wolfram
from utils.latex_converter import print_in_latex


def is_remove_small_with_parameters(term):
    smallness = base_remove_current_and_above_smallness(term, 2, small_variables=[C_Mx, C_My])
    if smallness >= 2:
        return True
    return False


def _sub_step_of_remove_small_params(_term, _order, _small_param):
    count = 0
    for sub_term in _term.args:
        if type(sub_term) == Pow and type(sub_term.args[0]) == Derivative:
            derivative = sub_term.args[0]
            variable = derivative.args[0]
            if variable in _small_param:
                count += sub_term.args[1]
                if count >= _order:
                    return count
        elif type(sub_term) == Derivative:
            variable = sub_term.args[0]
            if variable in _small_param:
                count += 1
                if count >= _order:
                    return count
    return count


def is_remove_small_term_with_velocities(term, small_coordinates=None):
    if small_coordinates is None:
        small_coordinates = [x, y, x1, x2, x3, x4, x5, x6, x7, x8]

    order = 2
    count = base_remove_current_and_above_smallness(term, order=order)
    if count >= order:
        return True

    count += _sub_step_of_remove_small_params(term, _order=order, _small_param=small_coordinates)
    if count >= order:
        return True

    # удаляем выше второго порядка малости члены содержащие x20, x30 (x70 = x20, x80 = x30)
    order_small_started_position = base_remove_current_and_above_smallness(term, order=order, small_variables=[x20, x30])
    if order_small_started_position >= order:
        return True

    return False


def print_ENERGY(energyExpr, name=None):
    ENERGY = simplification_expression(expand(energyExpr, deep=True))
    simplified_eq_i = 0
    for term_of_eq_i in ENERGY.args:
        if not is_remove_small_term_with_velocities_KIN_ENERGY(term_of_eq_i):
            simplified_eq_i += term_of_eq_i

    simplified_eq_i = simplify(expand_and_collect_term_before_squared_derivatives(simplified_eq_i), rational=True)

    print("======================================")
    print(name, " ENERGY IN WOLFRAM STYLE")
    print(Wolfram().transformForWolframMathematica(str(simplified_eq_i)))
    print(name, "ENERGY IN LATEX STYLE")
    print(print_in_latex(simplified_eq_i))
    print("======================================")

def is_remove_small_term_with_velocities_KIN_ENERGY(term, small_coordinates=None):
    if small_coordinates is None:
        small_coordinates_diff = [diff(x, t), diff(y, t), diff(x1, t), diff(x2, t), diff(x3, t),
                             diff(x4, t), diff(x5, t), diff(x6, t), diff(x7, t), diff(x8, t)]
        small_coordinates = [x, y, x1, x2, x3, x4, x5, x6, x7, x8]

    order = 2
    count = base_remove_current_and_above_smallness(term, order=order)
    if count >= order:
        return True

    dict_diff_to_order = {}
    haveSimplTerm = False
    for subterm in term.args:
        if subterm in small_coordinates:
            haveSimplTerm = True
        elif type(subterm) is Pow and len(subterm.args) == 2:
            var, pow = subterm.args
            if var in small_coordinates_diff:
                dict_diff_to_order[var] = pow
        elif subterm in small_coordinates_diff:
            dict_diff_to_order[subterm] = 1

    return len(dict_diff_to_order) > 1 or (haveSimplTerm and len(dict_diff_to_order) > 1)


def base_remove_current_and_above_smallness(term, order, small_variables=None):
    if small_variables is None:
        small_variables = [x, y, x1, x2, x3, x4, x5, x6, x7, x8]

    count = 0
    if type(term) == Derivative:
        return count

    for tterm in term.args:
        if count >= order:
            break
        if tterm in small_variables:
            count += 1
        elif type(tterm) is Pow and len(tterm.args) == 2:
            var, pow = tterm.args
            if var in small_variables:
                count += pow
    return count


def remove_fourth_and_above_smallness_from_one_term(term):
    if base_remove_current_and_above_smallness(term, 4) < 4:
        return term
    else:
        return 0


def remove_current_and_above_smallness_from_one_term(term, order, small_params=None):
    if base_remove_current_and_above_smallness(term, order, small_variables=small_params) < order:
        return term
    else:
        return 0


def __is_denominator_sym(symbol):
    return symbol in [d_phi_bot, d_eps_bot, d_tau_bot, d_del_bot, d_d_phi_bot, d_d_eps_bot, d_d_tau_bot, d_d_del_bot]


def remove_required_and_above_smallness_from_expression(expression, order, small_params=None):
    simplified = Zero()

    if type(expression) in (Symbol, One, NegativeOne, Derivative, Number, Integer) \
            or (type(expression) is Pow and type(expression.args[0]) is Symbol):
        return expression

    if type(expression) == Mul:
        smallness_order = base_remove_current_and_above_smallness(expression, order, small_variables=small_params)
        if smallness_order < order:
            return expression
        else:
            return 0

    for term in expand(expression).args:
        count = base_remove_current_and_above_smallness(term, order, small_variables=small_params)
        if count < order:
            try:
                simplified += term
            except:
                print("error in remove_required_and_above_smallness_from_expression")
    return simplified


def remove_required_and_above_smallness_from_expression_v2(expression, order):
    simplified = Zero()

    if type(expression) in (Symbol, One, Derivative, Integer) \
            or (type(expression) is Pow and type(expression.args[0]) is Symbol):
        return expression

    if type(expression) == Mul:
        smallness_order = base_remove_current_and_above_smallness(expression, order)
        if smallness_order < order:
            return expression
        else:
            return 0

    for term in expand(expression).args:
        count1 = base_remove_current_and_above_smallness(term, order)
        count2 = base_remove_current_and_above_smallness(term, 10, small_variables=[C_Mx, C_My, C_Mz])
        if count1 < order and count2 < 10:
            try:
                simplified += term
            except:
                print()
    return simplified

def remove_fourth_and_above_smallness_from_expression(expression):
    simplified = Zero()
    # if (type(expression) == Pow and __is_denominator_sym(expression.args[0])) or __is_denominator_sym(expression):
    #     return expression
    for term in expand(expression).args:
        count = base_remove_current_and_above_smallness(term, 4)
        if count < 4:
            simplified = Add(term, simplified)
    return simplified


def remove_third_and_above_smallness_from_one_term(term):
    if base_remove_current_and_above_smallness(term, 3) < 3:
        return term
    else:
        return 0


def remove_third_and_above_smallness_from_expression(expression):
    if expression == 1:
        return 1
    simplified = Zero()
    # if (type(expression) == Pow and __is_denominator_sym(expression.args[0])) or __is_denominator_sym(expression):
    #     return expression
    for term in expand(expression).args:
        count = base_remove_current_and_above_smallness(term, 3)
        if count < 3:
            simplified = Add(term, simplified)
    return simplified


def get_count_files_in_directory(path):
    import os
    count = 0
    for entry in os.listdir(path):
        if os.path.isfile(os.path.join(path, entry)):
            count += 1
    return count


def simplification_expression(expression, offset=False):
    """ упрощаем в предположении, что  α, γ и τ  мал """  # β
    trig_replace_dict = {
        cos(x1): 1,
        sin(x1): x1,

        cos(x2): 1,
        sin(x2): x2,

        cos(x3): 1,
        sin(x3): x3,

        cos(x5): 1,
        sin(x5): x5,

        cos(x6): 1,
        sin(x6): x6,

        cos(x7): 1,
        sin(x7): x7,

        cos(x8): 1,
        sin(x8): x8
    }
    if offset:
        trig_replace_dict[cos(x2)] = 1 - x2 * x20
        trig_replace_dict[cos(x3)] = 1 - x3 * x30

        trig_replace_dict[sin(x2)] = x20 + x2
        trig_replace_dict[sin(x3)] = x30 + x3

        trig_replace_dict[cos(x7)] = 1 - x2 * x20  # 1 - x7 * x70
        trig_replace_dict[cos(x8)] = 1 - x3 * x30  # 1 - x8 * x80

        trig_replace_dict[sin(x7)] = x20 + x2  # x70 + x7
        trig_replace_dict[sin(x8)] = x30 + x3  # x80 + x8

        # trig_replace_dict[cos(x2)] = cos(x20) - x2 * sin(x20)
    #         trig_replace_dict[cos(x3)] = cos(x30) - x3 * sin(x30)
    #
    #         trig_replace_dict[sin(x2)] = sin(x20) + x2 * cos(x20)
    #         trig_replace_dict[sin(x3)] = sin(x30) + x3 * cos(x30)
    #
    #         trig_replace_dict[cos(x7)] = cos(x70) - x7 * sin(x70)
    #         trig_replace_dict[cos(x8)] = cos(x80) - x8 * sin(x80)
    #
    #         trig_replace_dict[sin(x7)] = sin(x70) + x7 * cos(x70)
    #         trig_replace_dict[sin(x8)] = sin(x80) + x8 * cos(x80)

    simpl_raw = expression.subs(
        trig_replace_dict
    )
    return simpl_raw


def _add_simplify(coefficient, var):
    return Mul(
        trigsimp(coefficient),
        var
    )

def simplify_matrix(matrix, order=1):
    B_simpl = Matrix([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])

    for row_i in range(matrix.rows):
        row = Matrix([range(size_generic_vars)])

        for col_i in range(matrix.cols):
            row[col_i] = remove_required_and_above_smallness_from_expression(
                simplification_expression(matrix.row(row_i).col(col_i)[0]), order=order
            )
        B_simpl = B_simpl.row_insert(row_i+1, row)
    B_simpl.row_del(0)
    return B_simpl

def simplify_determinant(det_expression):
    list = []
    coefficients = [C_Mx ** 6, C_Mx ** 5, C_Mx ** 4, C_Mx ** 3, C_Mx ** 2, C_Mx,
                    C_My ** 6, C_My ** 5, C_My ** 4, C_My ** 3, C_My ** 2, C_My]
    for var in itertools.combinations(coefficients, 2):
        list.append(var[0] * var[1])

    list.append(C_Mx)
    list.append(C_My)
    list.append(C_Mx**2)
    list.append(C_My**2)
    list.extend([C_mz**4, C_mz**3, C_Mz ** 2, C_mz ** 2, C_Mz, C_mz, R**4, R**3, R**2, R])

    res = 0
    for coefficient in list:
        part = collect(det_expression, coefficient).coeff(coefficient)
        det_expression = sympify(det_expression - expand(Mul(part, coefficient)))
        inner_res = part
        simpl_inner_res = 0
        for inner_coefficient in [C_mz**4, C_mz**3, C_Mz ** 2, C_mz ** 2, C_Mz, C_mz, R**4, R**2, R]:
            inner_part = collect(inner_res, inner_coefficient).coeff(inner_coefficient)
            inner_res = sympify(inner_res - expand(Mul(inner_part, inner_coefficient)))
            simpl_inner_res += sympify(inner_part) * inner_coefficient
        res += (simpl_inner_res + inner_res) * coefficient
    return res + det_expression


def simplify_free_term(expression):
    free_symbols = [M_φ, M_ψ, x1, x2, x3, x6, x7, x8]
    other = [C_Mz ** 6, C_mz ** 6, C_Mz ** 5, C_mz ** 5, C_Mz ** 4, C_mz ** 4,
             C_Mz ** 3, C_mz ** 3, R ** 4, r ** 4, C_Mz ** 2, C_mz ** 2, R ** 2,
             C_Mx ** 6, C_Mx ** 5, C_Mx ** 4, C_Mx ** 3, C_Mx ** 2,
             C_My ** 6, C_My ** 5, C_My ** 4, C_My ** 3, C_My ** 2,
             r ** 2, J_px ** 2, J_py ** 2, J_wx ** 2, J_wy ** 2, J_px, J_py, J_wx, J_wy, C_Mz, C_mz]
    res = 0
    for coefficient in free_symbols:
        part = collect(expression, coefficient).coeff(coefficient)
        expression = sympify(expression - expand(Mul(part, coefficient)))
        inner_res = part
        simpl_inner_res = 0
        for inner_coefficient in other:
            inner_part = collect(inner_res, inner_coefficient).coeff(inner_coefficient)
            inner_res = sympify(inner_res - expand(Mul(inner_part, inner_coefficient)))
            simpl_inner_res += sympify(inner_part) * inner_coefficient
        res += (simpl_inner_res + inner_res) * coefficient
    return res + expression

def expand_and_collect_term_before_derivatives_and_lambda(expression):
    bedin = time.time()
    # expression = nsimplify(simplification_expression(expand(expression)), rational=True)
    print(expression)
    print("begin ", len(str(expression)))
    simplified = 0

    # коэффициенты перед diff(diff(var, t), t)
    for d_d_var in second_diff_generic_coord:
        before_second_diff = collect(expression, d_d_var).coeff(d_d_var)
        if type(before_second_diff) is Symbol or not before_second_diff._eval_is_zero():
            print(d_d_var, ": ", before_second_diff)
            expression = sympify(expression - expand(Mul(before_second_diff * d_d_var)))
            simplified = Add(simplified, _add_simplify(before_second_diff, d_d_var))

    print("time collect second derivatives %.2f [m]" % ((time.time() - bedin) / 60))
    print("middle1 ", len(str(expression)))

    # коэффициенты перед diff(var_i, t) * diff(var_j, t)
    for d_one_d_another in mixed_diff_of_generic_coordinates:
        before_mixed_diff = collect(expression, d_one_d_another, exact=True).coeff(d_one_d_another)
        if type(before_mixed_diff) is Symbol or not before_mixed_diff._eval_is_zero():
            expression = sympify(expression - expand(Mul(before_mixed_diff, d_one_d_another)))
            sss = _add_simplify(before_mixed_diff, d_one_d_another)
            simplified = Add(simplified, sss)
            print("done collect before: ", d_one_d_another)

    print("time collect mixed first derivatives ", round((time.time() - bedin) / 60, 2))
    print("middle2 ", len(str(expression)))

    # коэффициенты перед λ_i
    for λ_i in λ:
        before_lambda = collect(expression, λ_i).coeff(λ_i)
        if before_lambda.is_Symbol or not before_lambda._eval_is_zero():
            expression = sympify(expression - expand(Mul(before_lambda, λ_i)))
            simplified = Add(simplified, _add_simplify(before_lambda, λ_i))

    print("begin free")
    free_term = simplify(
        trigsimp(expand(expression))
    )  # simplification_expression(simplify(expression - trigsimp(expand(simplified))))
    print("free ", free_term)
    simplified = Add(simplified, free_term)

    end = time.time()
    print("total time ", round((end - bedin) / 60, 2))
    return simplified


def expand_and_collect_term_before_squared_derivatives(expression):
    simplified = 0
    expression = expand(expression, deep=True)
    for squared in squared_diff_generic_coord:
        before_squared = collect(expression, squared).coeff(squared)
        if type(before_squared) is Symbol or not before_squared._eval_is_zero():
            expression = sympify(expression - expand(Mul(before_squared * squared)))
            simplified = Add(simplified, _add_simplify(before_squared, squared))

    free_term = simplify(expand(expression))
    simplified = Add(simplified, free_term)

    return simplified

def expand_and_collect_term_before_first_derivatives(expression):
    expression = expand(expression)
    simplified = 0

    # коэффициенты перед diff(var, t)
    for d_var in first_diff_generic_vars:
        before_second_diff = collect(expression, d_var).coeff(d_var)
        print(before_second_diff)
        if before_second_diff.is_Symbol or not before_second_diff._eval_is_zero():
            simplified = Add(simplified, Mul(trigsimp(before_second_diff), d_var))

    return simplified
