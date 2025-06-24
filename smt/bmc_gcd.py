#!/usr/bin/env python3

from z3 import *

def gcd_bmc(k):
    """
    Perform bounded model checking on the GCD algorithm, unrolled k steps.
    Looks for a violation where y_k == 0 but x_k != G,
    where G divides both x_0 and y_0.
    """
    solver = Solver()

    # Create symbolic variables for each step
    X = [Int(f'x_{i}') for i in range(k+1)]
    Y = [Int(f'y_{i}') for i in range(k+1)]
    
    # A symbolic candidate for gcd(x_0, y_0)
    G = Int('G')

    # Initial constraints: let x_0, y_0 > 0, and G is a positive integer dividing both
    solver.add(X[0] > 0, Y[0] > 0, G > 0)
    solver.add(X[0] % G == 0, Y[0] % G == 0)

    # Encode the transitions for i in [0..k-1]
    # Euclid's step: if x_i > y_i then (x_{i+1}, y_{i+1}) = (x_i - y_i, y_i)
    # otherwise (x_{i+1}, y_{i+1}) = (x_i, y_i - x_i)
    for i in range(k):
        solver.add(
            Or(
                And(X[i] > Y[i],
                    X[i+1] == X[i] - Y[i],
                    Y[i+1] == Y[i]),
                And(X[i] <= Y[i],
                    Y[i+1] == Y[i] - X[i],
                    X[i+1] == X[i])
            )
        )

    # Violation condition: at step k, y_k = 0 but x_k != G.
    # We ask if there's any solution (SAT) to that scenario
    solver.add(Y[k] == 0, X[k] != G)

    # Check for satisfiability
    result = solver.check()
    if result == sat:
        print(f"[BMC k={k}] Counterexample found!")
        print("Model (one possible assignment):")
        print(solver.model())
    else:
        print(f"[BMC k={k}] No counterexample found (UNSAT).")


def run_bmc_up_to(max_k):
    print("=== Bounded Model Checking (BMC) for GCD ===")
    for k in range(1, max_k+1):
        gcd_bmc(k)

if __name__ == "__main__":
    # Run bounded model checking from k = 1 to k = 5
    run_bmc_up_to(5)
