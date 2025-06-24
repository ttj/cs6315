#!/usr/bin/env python3

from z3 import *

def gcd_bmc_with_fixed_point(k):
    """
    Unroll the GCD loop k steps, then add a "fixed point" constraint
    at step k -> k+1, and check if there's a stable state that violates
    gcd correctness (i.e., y=0 but x != G).
    """

    solver = Solver()

    # Create symbolic variables for each step: x_i, y_i for i in [0..k+1]
    # We'll have (k+2) states in total: 0..k plus the "fixed" state k+1.
    X = [Int(f'x_{i}') for i in range(k+2)]
    Y = [Int(f'y_{i}') for i in range(k+2)]

    # A symbolic candidate for gcd(x_0, y_0)
    G = Int('G')

    # -------------------------------------
    # 1) Initial constraints
    # -------------------------------------
    solver.add(X[0] > 0, Y[0] > 0, G > 0)
    solver.add(X[0] % G == 0, Y[0] % G == 0)

    # -------------------------------------
    # 2) Encode standard Euclid transitions for i in [0..k-1]
    #    (these are the "unrolled" steps)
    # -------------------------------------
    #   if x_i > y_i:
    #       (x_{i+1}, y_{i+1}) = (x_i - y_i, y_i)
    #   else:
    #       (x_{i+1}, y_{i+1}) = (x_i, y_i - x_i)
    for i in range(k):
        solver.add(
            Or(
                And(X[i] > Y[i],
                    X[i+1] == X[i] - Y[i],
                    Y[i+1] == Y[i]),
                And(X[i] <= Y[i],
                    X[i+1] == X[i],
                    Y[i+1] == Y[i] - X[i])
            )
        )

    # -------------------------------------
    # 3) Fixed-point constraint at step k -> k+1
    #    i.e. (x_{k+1}, y_{k+1}) = (x_k, y_k)
    # -------------------------------------
    solver.add(X[k+1] == X[k], Y[k+1] == Y[k])

    # -------------------------------------
    # 4) "Violation" condition:
    #    We want to see if there's a stable state with y=0 but x != G.
    #    That is, at step (k+1), if y_{k+1} == 0 but x_{k+1} != G,
    #    do we have a model (SAT)?
    # -------------------------------------
    solver.add(Y[k+1] == 0, X[k+1] != G)

    # -------------------------------------
    # 5) Check satisfiability
    # -------------------------------------
    result = solver.check()
    if result == sat:
        print(f"[Fixed-Point BMC k={k}] Found a stable state violating gcd!")
        print("Model (one possible assignment):")
        print(solver.model())
    else:
        print(f"[Fixed-Point BMC k={k}] UNSAT - No bad stable state found.")

def run_bmc_fixed_up_to(max_k):
    print("=== Bounded Model Checking (with Fixed-Point Step) for GCD ===")
    for k in range(1, max_k+1):
        gcd_bmc_with_fixed_point(k)

if __name__ == "__main__":
    run_bmc_fixed_up_to(25)
