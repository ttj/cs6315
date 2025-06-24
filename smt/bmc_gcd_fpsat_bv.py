#!/usr/bin/env python3

from z3 import *

def gcd_bmc_with_fixed_point_bv(k):
    """
    Unroll the GCD loop k steps, then add a 'fixed point' constraint
    at step k -> k+1, using 5-bit BitVecs instead of Ints.

    Check if there's a stable state (y_{k+1} = y_k, x_{k+1} = x_k)
    where y=0 but x != G (meaning the stored 'gcd candidate' is violated).
    """

    solver = Solver()

    # Define 5-bit bitvector sort
    BV5 = BitVecSort(5)

    # Create symbolic 5-bit variables for each step: x_i, y_i for i in [0..k+1]
    # We'll have (k+2) states in total: 0..k plus the "fixed" state k+1.
    X = [BitVec(f'x_{i}', 5) for i in range(k+2)]
    Y = [BitVec(f'y_{i}', 5) for i in range(k+2)]

    # A 5-bit symbolic candidate for gcd(x_0, y_0)
    G = BitVec('G', 5)

    # -------------------------------------
    # 1) Initial constraints:
    #    - x_0, y_0, and G are non-zero in 5-bit sense
    #    - G divides x_0 and y_0 in the bitvector sense (x_0 % G == 0)
    #
    # Note: We use UGT(x_0,0) to say it's not zero. Alternatively, we could do x_0 != 0.
    # Similarly for G != 0 to avoid division by zero in URem.
    # -------------------------------------
    solver.add(X[0] != 0, Y[0] != 0, G != 0)

    # For "G divides x_0 and y_0", we use the unsigned remainder URem:
    # (Z3 uses 'URem' for bitvector remainder.)
    solver.add(URem(X[0], G) == 0)
    solver.add(URem(Y[0], G) == 0)

    # -------------------------------------
    # 2) Encode standard Euclid transitions (k steps)
    #
    #   if x_i > y_i:
    #       x_{i+1} = x_i - y_i  (bitvector subtraction)
    #       y_{i+1} = y_i
    #   else:
    #       x_{i+1} = x_i
    #       y_{i+1} = y_i - x_i
    #
    # But ">" becomes an unsigned BV comparison: UGT(x_i, y_i)
    # -------------------------------------
    for i in range(k):
        solver.add(
            Or(
                And(
                    UGT(X[i], Y[i]),
                    X[i+1] == X[i] - Y[i],  # BVSub
                    Y[i+1] == Y[i]
                ),
                And(
                    Not(UGT(X[i], Y[i])),  # means x_i <= y_i (unsigned)
                    X[i+1] == X[i],
                    Y[i+1] == Y[i] - X[i]
                )
            )
        )

    # -------------------------------------
    # 3) Fixed-point constraint at step k -> k+1
    #
    #    (x_{k+1}, y_{k+1}) = (x_k, y_k)
    #
    # This forces the state not to change after step k.
    # -------------------------------------
    solver.add(X[k+1] == X[k], Y[k+1] == Y[k])

    # -------------------------------------
    # 4) "Violation" condition:
    #
    #    We want a stable state (the final state) with y=0 but x != G.
    # -------------------------------------
    solver.add(Y[k+1] == 0, X[k+1] != G)

    # -------------------------------------
    # 5) Check satisfiability
    # -------------------------------------
    result = solver.check()
    if result == sat:
        print(f"[Fixed-Point BMC (BV5) k={k}] Found a stable state violating gcd!")
        model = solver.model()
        print("Model (one possible assignment):")
        print(model)
        # Optionally show numeric values for X_i, Y_i, G
        print("Interpreted values:")
        for d in model.decls():
            print(f"{d.name()} =", model[d].as_long(), "(decimal)")
    else:
        print(f"[Fixed-Point BMC (BV5) k={k}] UNSAT - No bad stable state found.")


def run_bmc_fixed_bv_up_to(max_k):
    """
    Try the fixed-point BMC check with 5-bit bitvectors for k from 1..max_k.
    """
    print("=== Bounded Model Checking (with Fixed-Point Step) for GCD (5-bit BV) ===")
    for k in range(1, max_k+1):
        gcd_bmc_with_fixed_point_bv(k)
    print("Done.")


if __name__ == "__main__":
    run_bmc_fixed_bv_up_to(5)
