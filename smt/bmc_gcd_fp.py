#!/usr/bin/env python3

from z3 import *

def gcd_fixedpoint_demo():
    """
    Demonstrates using Z3's fixedpoint engine with Horn clauses
    to encode reachability in the Euclid GCD transition system.
    We query if there's a reachable state with y=0 and x != 1.
    (This is just a toy property to show how to use Fixedpoint.)
    """
    # Declare sorts (integers)
    x, y, x0, y0 = Ints('x y x0 y0')

    # Relation R(x, y, x0, y0):
    #   means (x, y) is reachable from the initial (x0, y0).
    R = Function('R', IntSort(), IntSort(), IntSort(), IntSort(), BoolSort())

    fp = Fixedpoint()
    fp.register_relation(R)
    fp.declare_var(x, y, x0, y0)

    # 1) Initial rule: from (x0, y0) we can reach itself
    #    R(x0, y0, x0, y0)
    fp.rule(
        R(x0, y0, x0, y0),
        []
    )

    # 2) Transition rules:
    #    if R(x, y, x0, y0) and y != 0 and x > y,
    #    then R(x-y, y, x0, y0).
    fp.rule(
        R(x - y, y, x0, y0),
        [R(x, y, x0, y0), y != 0, x > y]
    )

    #    if R(x, y, x0, y0) and y != 0 and x <= y,
    #    then R(x, y-x, x0, y0).
    fp.rule(
        R(x, y - x, x0, y0),
        [R(x, y, x0, y0), y != 0, x <= y]
    )

    # 3) Query: Is there a reachable state with y=0 and x != 1?
    #    i.e., does there exist x, y, x0, y0 s.t. R(x, y, x0, y0), y=0, x!=1?
    query = Exists([x, y, x0, y0], And(R(x, y, x0, y0), y == 0, x != 1))

    res = fp.query(query)

    print("=== Fixedpoint Query ===")
    print("Asking if there's a reachable state with y=0 and x != 1...")
    print("Result:", res)  # sat, unsat, or unknown
    if res == sat:
        # If SAT, we can retrieve a 'witness'
        print("Model (witness to a bad state):")
        print(fp.get_answer())
    else:
        print("No such state is reachable (given the constraints).")


if __name__ == "__main__":
    # Simple demonstration of the fixedpoint approach
    gcd_fixedpoint_demo()
